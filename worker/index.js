export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // --- 辅助函数：获取用户元数据 ---
    async function getUserData(key) {
      const value = await env.USERS.get(key);
      if (!value) return null;
      
      // 兼容旧版 "active" 字符串
      if (value === "active") {
        return { status: "active", expires_at: null, name: "Legacy User" };
      }
      
      try {
        return JSON.parse(value);
      } catch (e) {
        return { status: "error", message: "Invalid Metadata" };
      }
    }

    // --- 1. 处理 /setup 页面 ---
    if (url.pathname === "/setup") {
      const urlKey = url.searchParams.get("key");
      const userData = await getUserData(urlKey);

      if (!userData || userData.status !== "active") {
        return new Response("Unauthorized: Invalid or Inactive Key", { status: 403 });
      }

      // 检查过期时间
      if (userData.expires_at && new Date() > new Date(userData.expires_at)) {
        return new Response("Expired: Your access has expired. Please contact Rick.", { status: 403 });
      }

      const setupHeaders = new Headers();
      setupHeaders.set("CF-Access-Client-Id", env.CF_CLIENT_ID);
      setupHeaders.set("CF-Access-Client-Secret", env.CF_CLIENT_SECRET);
      setupHeaders.set("X-Bridge-Secret", env.BRIDGE_INTERNAL_SECRET);
      
      // 将元数据透传给后端展示和逻辑分流
      if (userData.name) setupHeaders.set("X-User-Name", encodeURIComponent(userData.name));
      if (userData.expires_at) setupHeaders.set("X-User-Expires", userData.expires_at);
      if (userData.tier) setupHeaders.set("X-User-Tier", userData.tier);

      return fetch(`https://siri.961213.xyz/setup?key=${urlKey}`, { headers: setupHeaders });
    }

    // --- 1.0 处理产品主页 (/) ---
    if (url.pathname === "/") {
      const homeHeaders = new Headers();
      homeHeaders.set("CF-Access-Client-Id", env.CF_CLIENT_ID);
      homeHeaders.set("CF-Access-Client-Secret", env.CF_CLIENT_SECRET);
      homeHeaders.set("X-Bridge-Secret", env.BRIDGE_INTERNAL_SECRET);

      return fetch("https://siri.961213.xyz/", { headers: homeHeaders });
    }

    // --- 1.1 处理 /admin/provision 接口 (企业级自动化发码) ---
    if (url.pathname === "/admin/provision") {
      const adminHeaders = new Headers(request.headers);
      adminHeaders.set("CF-Access-Client-Id", env.CF_CLIENT_ID);
      adminHeaders.set("CF-Access-Client-Secret", env.CF_CLIENT_SECRET);
      adminHeaders.set("X-Bridge-Secret", env.BRIDGE_INTERNAL_SECRET);

      const modifiedRequest = new Request(`https://siri.961213.xyz/admin/provision${url.search}`, {
        method: request.method,
        headers: adminHeaders,
        body: request.body,
      });

      return fetch(modifiedRequest);
    }

    // --- 2. 处理 /ask 接口 ---
    const authHeader = request.headers.get("Authorization");
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return new Response("Unauthorized: Missing sk-key", { status: 401 });
    }
    const userApiKey = authHeader.split(" ")[1];

    const userData = await getUserData(userApiKey);
    if (!userData || userData.status !== "active") {
      return new Response("Unauthorized: Invalid API Key", { status: 403 });
    }

    // 检查有效期
    if (userData.expires_at && new Date() > new Date(userData.expires_at)) {
      return new Response("Unauthorized: Key Expired", { status: 403 });
    }

    const newHeaders = new Headers(request.headers);
    newHeaders.set("CF-Access-Client-Id", env.CF_CLIENT_ID);
    newHeaders.set("CF-Access-Client-Secret", env.CF_CLIENT_SECRET);
    newHeaders.set("X-Bridge-Secret", env.BRIDGE_INTERNAL_SECRET);
    
    // 透传等级信息给后端进行路由分发
    if (userData.tier) newHeaders.set("X-User-Tier", userData.tier);

    const targetUrl = new URL(request.url);
    targetUrl.hostname = "siri.961213.xyz";

    const modifiedRequest = new Request(targetUrl, {
      method: request.method,
      headers: newHeaders,
      body: request.body,
    });

    return fetch(modifiedRequest);
  },
};
