// Login helpers shared by every page.

function getToken() {
  try { return sessionStorage.getItem("shc_token") || ""; } catch (e) { return ""; }
}

function setToken(token) {
  try { sessionStorage.setItem("shc_token", token); } catch (e) {}
}

function clearToken() {
  try { sessionStorage.removeItem("shc_token"); } catch (e) {}
}

// Put on a page that needs a logged-in doctor: sends visitors to the login page.
function requireLogin() {
  if (!getToken()) { window.location.replace("login.html"); }
}

function logout() {
  clearToken();
  window.location.href = "login.html";
}

// Like fetch(), but adds the login token. If the backend says 401, go back to login.
function authFetch(url, options) {
  options = options || {};
  options.headers = options.headers || {};
  options.headers["Authorization"] = "Bearer " + getToken();
  return fetch(url, options).then(function (res) {
    if (res.status === 401) {
      clearToken();
      window.location.replace("login.html");
    }
    return res;
  });
}