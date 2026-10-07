# One-page POS demo (Airwallex Terminals)

Unofficial demo: a retail / F&B order page that totals a cart, creates a Payment Intent and pushes it to an
Airwallex terminal (`process_payment_intent`), then shows the result and a payment history.

**Not an official Airwallex sample. Never put API keys or create Payment Intents in front-end code in production.**

## Deploy on GitHub Pages (2 parts, ~5 minutes)

### 1. Deploy the proxy once (free Cloudflare Worker)
Airwallex does not allow browser (CORS) calls to the payment-intent and terminal endpoints, so the page talks to
Airwallex through a tiny pass-through. It forwards requests unchanged, adds CORS headers and stores nothing.
1. Cloudflare dashboard → **Workers & Pages → Create → Create Worker** → **Deploy** the hello-world, then **Edit code**.
2. Paste the contents of `cloudflare-worker.js` → **Deploy**.
3. Copy the URL, e.g. `https://awx-pos-proxy.yourname.workers.dev`.
4. Recommended: in the worker set `ALLOW_ORIGIN` to your Pages origin (e.g. `https://yourname.github.io`) and redeploy,
   so only your page can use it.

### 2. Publish the page
1. In `index.html` set `DEFAULT_PROXY = 'https://awx-pos-proxy.yourname.workers.dev'` (so visitors need no setup),
   or leave it empty and paste the URL into **Setup → API proxy URL**.
2. Push this folder to a GitHub repo → **Settings → Pages → Deploy from branch → `main` / `(root)`**.
3. Open `https://<you>.github.io/<repo>/`, enter demo credentials, press **Test credentials**, then **Load terminals**.

## Run locally (instead of `python -m http.server`)
`python -m http.server` only handles GET, so Airwallex POST calls fail with **501**. Use the bundled script, which serves the page
and forwards the API calls on the same port (standard library only):
```
python3 local_server.py          # then open http://localhost:8000
```
In **Setup → API proxy URL** enter `http://localhost:8000`.

## Setup in the page
Logo + store name, environment (Demo/Production), currency, Client ID, API key (optionally saved in localStorage),
connected account ID (optional; sent as `connected_account_id` on the terminal list and the Payment Intent — no `x-on-behalf-of`), proxy URL. **Test credentials** checks login and the Terminals API.

## Images (lowercase file names, PNG, ~600×600 square)
```
assets/logo-default.png                 optional default logo
assets/retail/  tee hoodie sneakers cap tote-bag sunglasses watch backpack   (.png)
assets/fnb/     burger fries ramen salad milk-tea coffee cola cheesecake     (.png)
```
GitHub Pages is case-sensitive. Missing images show a placeholder tile. Items and prices live in the `CATALOG` object.

## Demo environment
While a payment is waiting, **Simulate customer tap** calls the simulation endpoints so you can demo without a physical terminal.
