import http from 'k6/http';
import { check } from 'k6';

const target = __ENV.TARGET_URL || 'http://127.0.0.1:8000/slow';

export const options = {
  vus: 5,
  duration: '1m',
};

export default function () {
  const res = http.get(target);
  check(res, { 'status 200 байна': (r) => r.status === 200 });
}
