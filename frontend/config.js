// Backend address. Local testing uses your laptop, the live site uses Render.
var API = (location.hostname === "127.0.0.1" || location.hostname === "localhost")
  ? "http://127.0.0.1:8000"
  : "https://smart-health-card-api.onrender.com";