# k6-аар гүйцэтгэл хэмжих лаборатори

**Хичээл:** F.CSA313 — Программ хангамжийн чанарын баталгаа ба тест (2026)  
**Хэмжилтийн өдөр:** 2026-11-21  
**k6 хувилбар:** `k6 v2.4.0 (commit/dd9395906d, go1.26.11, darwin/arm64)`

## Туршилтын орчин

Зөвшөөрөгдсөн локал бай `http://127.0.0.1:8000/slow` дээр туршив. `local_server.py` нь нэг хүсэлтэд 100 мс зориуд хүлээлгэдэг бөгөөд зэрэг 10 хүсэлтэд л үйлчилнэ; үлдсэн холболтыг серверийн worker slot сулрах хүртэл хүлээлгэнэ. Туршилт гадаад сайт руу хүсэлт илгээгээгүй.

Серверийг нэг терминалд асаагаад, энэ хавтаснаас доорх командыг ажиллуулна:

```sh
python3 local_server.py
```

`k6` binary-г Grafana-ийн албан ёсны macOS ARM64 release-ээс ашиглав. Скрипт бүрийн үндсэн URL localhost; өөр URL хэрэглэх шаардлагагүй.

## 5 VU baseline

Алхам 2-ын `script.js`-ийг 5 VU, 1 минут ажиллуулсан. Суурь p95 нь **106.38 ms**; энэ хэмжилтийг SLO тогтооход ашиглав.

## Ачааллын хэмжилт

| VU | p90 latency | p95 latency | Throughput (`http_reqs`) | Error rate (`http_req_failed`) |
|---:|---:|---:|---:|---:|
| 5 | 106.17 ms | 106.38 ms | 47.672489 req/s | 0.00% (0/2863) |
| 30 | 314.39 ms | 315.58 ms | 96.433931 req/s | 0.00% (0/5816) |
| 100 | 1.04 s | 1.74 s | 96.763767 req/s | 0.10% (6/5904) |

Тоо бүрийг `results/run-05vu.txt`, `results/run-30vu.txt`, `results/run-100vu.txt` файлын бүтэн k6 summary-тай тулгаж болно. Тэр файлууд нь тухайн туршилтын шууд текст гаралт юм. Давтан ажиллуулах командууд:

```sh
k6 run --vus 5 --duration 1m script.js | tee results/run-05vu.txt
k6 run --vus 30 --duration 1m script.js | tee results/run-30vu.txt
k6 run --vus 100 --duration 1m script.js | tee results/run-100vu.txt
k6 run stages.js | tee results/run-stages.txt
P95_LIMIT_MS=160 k6 run thresholds.js | tee results/threshold-pass.txt
P95_LIMIT_MS=50 k6 run thresholds.js | tee results/threshold-fail.txt
```

### Stages туршилт

5 VU-ээс 30, 100 VU хүртэл өсгөж бууруулсан run-ийн **нэгтгэсэн** summary: p90 **871.19 ms**, p95 **958.65 ms**, throughput **78.665074 req/s**, алдаа **0.00% (0/11805)**. Энэ ганц p95 утгыг үе шат тус бүрийнх гэж үзээгүй; 5/30/100 VU-ийн хүснэгтийг тусдаа тогтмол ачааллын run-уудаас авсан. Бүтэн гаралт `results/run-stages.txt` файлд бий.

## SLO threshold

Latency SLO-г baseline p95 × 1.5 гэж авлаа: `106.38 ms × 1.5 = 159.57 ms`, бүхэл ms рүү дээш тоймлон **p95 < 160 ms** болгосон. Нэмэлт SLO нь хүсэлтийн алдааны хувь **1%-аас бага**. `thresholds.js` дотор p95 босгыг орчны хувьсагчаар өгдөг тул тухайн threshold-ийг гарцаар нь давхар бичихгүйгээр ижил скриптээр хоёр хувилбарыг шалгана.

- **PASS:** `P95_LIMIT_MS=160 k6 run thresholds.js` — p95 106.24 ms, error rate 0.00%; хоёр босгыг хангасан (`results/threshold-pass.txt`).
- **FAIL:** `P95_LIMIT_MS=50 k6 run thresholds.js` — p95 106.4 ms тул `p(95)<50` босгыг даваагүй; k6 threshold зөрчлийг тэмдэглэсэн (`results/threshold-fail.txt`).

## Дүгнэлт

1. 5 VU үед p95 latency 106.38 мс, throughput 47.67 req/s байв.
2. 30 VU болоход p95 315.58 мс болж, throughput 96.43 req/s хүрсэн.
3. 100 VU үед p95 1.74 сек болсон ч throughput 96.76 req/s орчимд тогтсон.
4. Ингэснээр ачаалал эхэнд throughput-ийг өсгөсөн ч серверийн 10 worker-ийн хязгаарт хүрээд өсөлт саарч байгааг харууллаа.
5. Үүний зэрэгцээ хүсэлтүүд worker сулрахыг хүлээсэн тул хэрэглэгчийн latency ихээр муудсан.
6. 100 VU-ийн run-д 6/5904 хүсэлт амжилтгүй болж, error rate 0.10% болсон.
7. Энэ нь лекцийн throughput ба latency-ийн trade-off, мөн ачааллын үед error rate нэмэгдэх ойлголтыг дэмжиж байна.
8. Stages run-ийн нэгтгэсэн p95 958.65 мс байсан бөгөөд оргил руу өсөх, буух хугацаанд latency хэлбэлзсэн.
9. Тогтоосон SLO нь p95 < 160 мс болон алдаа < 1%; baseline 5 VU PASS, 30 ба 100 VU-ийн хүснэгтийн latency p95 босгыг хангахгүй.

## Үр дүнгийн файлууд

`results/` хавтаст үндсэн гурван туршилтын бүтэн текст гаралт, stages summary, threshold-ийн PASS/FAIL гаралт хадгалагдсан. `screenshots/` дахь зурагнууд нь эдгээр жинхэнэ k6 гаралтаас дүрсэлсэн хураангуй юм; бүрэн, эх текст гаралт үр дүнгийн файлд үлдсэн.

- [5 VU summary](screenshots/summary-05vu.png)
- [30 VU summary](screenshots/summary-30vu.png)
- [100 VU summary](screenshots/summary-100vu.png)
