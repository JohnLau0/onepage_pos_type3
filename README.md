# One-page POS demo (Airwallex Terminals)

A single static page that looks like a F&B / retail order screen. Pick items, the page totals the order, creates an
Airwallex Payment Intent, sends it to a terminal with
[`process_payment_intent`](https://www.airwallex.com/docs/api/payments/terminals/process_payment_intent), polls for the
result and keeps a payment history.

> **Unofficial demo. This is not an official Airwallex sample.**
> Do not implement it this way in production: never put API keys / client secrets in front-end code, and never create or
> confirm Payment Intents from the browser. Do that on your server. Use **demo** credentials only.

## How it works

```
index.html (GitHub Pages)  ──►  proxy (Cloudflare Worker)  ──►  Airwallex API  ──►  terminal
```

1. **Login:** `POST /api/v1/authentication/login` with your Client ID and API key, then a Bearer token (cached ~30 min).
2. **List terminals:** `GET /api/v1/pa/pos/terminals` (optionally filtered by `connected_account_id`).
3. **Charge:** `POST /api/v1/pa/payment_intents/create`, then
   `POST /api/v1/pa/pos/terminals/{id}/process_payment_intent`.
4. **Result:** `GET /api/v1/pa/payment_intents/{id}` every 1.5 s until `SUCCEEDED`, `CANCELLED` or `REQUIRES_CAPTURE`
   (3 minute timeout).
5. **Cancel:** the terminal's `cancel_current_operation` plus cancelling the Payment Intent.

Why a proxy: in my tests Airwallex answers browser CORS preflights on login and billing endpoints but not on the
`/pa/...` payment and terminal endpoints, so a static page cannot call those directly. The proxy forwards requests
unchanged, adds CORS headers and stores nothing.

## Features

- Setup: store logo + name, **F&B / Retail** toggle (F&B is the default), Demo / Production, currency, Client ID,
  API key, optional connected account ID, API proxy URL.
- **Test credentials** (login + a Terminals API call) and **Load terminals** with a terminal picker.
- Product grid, cart and a **Charge** button; **Cancel payment** while a payment is waiting.
- Payment result card with progress steps, plus buttons for **Check payment status now** and
  **Cancel current action on terminal**.
- Payment records table (saved in the browser, click a row for the raw Payment Intent) and an API call log
  (tokens and keys are masked).
- Demo environment: **Simulate customer tap** so you can try it without a physical terminal.

## Deploy on GitHub Pages

### 1. Deploy the proxy once (Cloudflare Worker)
1. Cloudflare dashboard → **Workers & Pages → Create → Create Worker** → deploy the hello-world → **Edit code**.
2. Paste the contents of [`cloudflare-worker.js`](cloudflare-worker.js) → **Deploy**.
3. Copy the worker URL, e.g. `https://something.workers.dev`.
4. Recommended: set `ALLOW_ORIGIN` in the worker to your Pages origin (e.g. `https://yourname.github.io`) and redeploy,
   so only your page can use it. Keep `'*'` while testing from `localhost`.

### 2. Publish the page
1. In `index.html` set `DEFAULT_PROXY = 'https://something.workers.dev'` so visitors need no setup, or leave it empty and
   paste the URL into **Setup → API proxy URL**.
2. Push the repo to GitHub → **Settings → Pages → Deploy from branch → `main` / `(root)`**.
3. Open `https://<you>.github.io/<repo>/`, enter demo credentials, click **Test credentials**, then **Load terminals**.

## Run locally

`python -m http.server` only handles GET, so Airwallex POST calls fail with **501**. Use the bundled script, which serves the
page and forwards API calls on the same port (Python standard library only):

```bash
python3 local_server.py          # then open http://localhost:8000
```

In **Setup → API proxy URL** enter `http://localhost:8000`. (Or point it at your deployed worker.)

## Images

Square PNGs, about 600×600, **lowercase** file names. GitHub Pages is case-sensitive.

```
assets/logo-default.png          optional default logo
assets/fnb/     burger fries ramen salad milk-tea coffee cola cheesecake     (.png)
assets/retail/  tee hoodie sneakers cap tote-bag sunglasses watch backpack   (.png)
```

Missing images show a coloured placeholder tile. Items and prices are in the `CATALOG` object at the top of the script
in `index.html`.

## Files

| File | Purpose |
|---|---|
| `index.html` | The whole app (HTML, CSS, JS, no build step) |
| `cloudflare-worker.js` | Pass-through proxy to deploy on Cloudflare |
| `local_server.py` | Local static server + proxy for testing |
| `assets/` | Your logo and product images |

## Notes

- Credentials stay in the browser. They are saved to localStorage only if you tick the checkbox, and **Clear saved data**
  removes them.
- Amounts use 2 decimals; polling uses `GET` only, so no webhooks or public URL are needed.
- Tested with a stubbed API; run it against your own demo account to confirm the live behaviour.
