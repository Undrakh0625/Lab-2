import http from 'k6/http';
import { check } from 'k6';

const target = __ENV.TARGET_URL || 'http://127.0.0.1:8000/slow';
const p95Limit = __ENV.P95_LIMIT_MS || '1000';

export const options = {
  vus: 5,
  duration: '1m',
  thresholds: {
    http_req_duration: [`p(95)<${p95Limit}`],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const res = http.get(target);
  check(res, { 'status 200 байна': (r) => r.status === 200 });
}
