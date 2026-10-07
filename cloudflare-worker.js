// Optional pass-through proxy so index.html can call Airwallex from the browser (CORS).
// Deploy: Cloudflare dashboard -> Workers & Pages -> Create Worker -> paste this -> Deploy.
// Then put the worker URL in the page's "API proxy URL" field, e.g. https://awx-pos-proxy.<you>.workers.dev
//
// The page calls  <proxy>/demo/api/v1/...  or  <proxy>/prod/api/v1/...
// It forwards the request (including the Authorization / x-api-key headers) to Airwallex unchanged
// and adds CORS headers. It stores nothing. Demo use only.

const TARGETS = {
  demo: 'https://api-demo.airwallex.com',
  prod: 'https://api.airwallex.com',
};

// Lock this down to your GitHub Pages origin, e.g. 'https://yourname.github.io'
const ALLOW_ORIGIN = '*';

const CORS = {
  'access-control-allow-origin': ALLOW_ORIGIN,
  'access-control-allow-methods': 'GET,POST,OPTIONS',
  'access-control-allow-headers': 'authorization,content-type,x-client-id,x-api-key,x-on-behalf-of,x-login-as',
  'access-control-max-age': '86400',
};

export default {
  async fetch(req) {
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS });

    const url = new URL(req.url);
    const [, env, ...rest] = url.pathname.split('/');
    const target = TARGETS[env];
    if (!target || !rest.length) {
      return new Response('Use /demo/api/v1/... or /prod/api/v1/...', { status: 404, headers: CORS });
    }

    const headers = new Headers(req.headers);
    for (const h of ['host', 'origin', 'referer']) headers.delete(h);

    const upstream = await fetch(`${target}/${rest.join('/')}${url.search}`, {
      method: req.method,
      headers,
      body: req.method === 'GET' || req.method === 'HEAD' ? undefined : req.body,
    });

    const out = new Response(upstream.body, upstream);
    for (const [k, v] of Object.entries(CORS)) out.headers.set(k, v);
    return out;
  },
};
