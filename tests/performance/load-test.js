import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up to 10 users over 2 minutes
    { duration: '5m', target: 10 }, // Stay at 10 users for 5 minutes
    { duration: '2m', target: 0 },  // Ramp down to 0 users over 2 minutes
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'], // 95% of requests must complete below 1s
    http_req_failed: ['rate<0.1'],     // Error rate must be below 10%
  },
};

export default function () {
  // Test health endpoint
  let response = http.get('http://localhost:8000/health');
  check(response, {
    'health endpoint status is 200': (r) => r.status === 200,
    'health endpoint response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);

  // Test root endpoint
  response = http.get('http://localhost:8000/');
  check(response, {
    'root endpoint status is 200': (r) => r.status === 200,
    'root endpoint response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);

  // Test API endpoints
  response = http.get('http://localhost:8000/api/v1/users/');
  check(response, {
    'users endpoint status is 200': (r) => r.status === 200,
    'users endpoint response time < 1000ms': (r) => r.timings.duration < 1000,
  });

  sleep(1);
}
