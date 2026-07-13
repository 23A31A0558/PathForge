// frontend/js/api.js

// Dynamic API Base URL resolution (port 8000 for backend during local development)
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000'
    : window.location.origin;

// Transparent global window.fetch Interceptor for detailed communication logging and safety audits
const originalFetch = window.fetch;
window.fetch = async function (resource, options) {
    const url = typeof resource === 'string' ? resource : resource.url;
    const method = (options && options.method) || 'GET';
    const payload = (options && options.body) || null;

    console.log(`[API REQUEST] Method: ${method} | URL: ${url}`);
    if (payload) {
        // Log request payloads safely
        if (payload instanceof URLSearchParams) {
            console.log(`[API REQUEST PAYLOAD (URLSearchParams)]`, Object.fromEntries(payload.entries()));
        } else {
            console.log(`[API REQUEST PAYLOAD]`, payload);
        }
    }

    try {
        const response = await originalFetch(resource, options);
        console.log(`[API RESPONSE STATUS] URL: ${url} | Status: ${response.status}`);

        // Clone the response stream to inspect response body safely without consuming the main stream
        const clone = response.clone();
        const responseText = await clone.text();
        console.log(`[API RESPONSE BODY] URL: ${url} | Body:`, responseText);

        // Intercept and wrap response.json() to prevent JSON parser syntax crashes when returning HTML/text
        const originalJson = response.json.bind(response);
        response.json = async function () {
            const contentType = response.headers.get("content-type") || "";
            if (!contentType.includes("application/json")) {
                console.error(`[API JSON PARSE ERROR] Expected JSON from ${url} but received content-type "${contentType}". Body:`, responseText);
                
                if (responseText.trim().startsWith("<!DOCTYPE") || responseText.trim().startsWith("<html")) {
                    throw new Error("Received HTML response instead of JSON. Server endpoint mismatch or error occurred.");
                }
                throw new Error(responseText || "Non-JSON response received.");
            }
            return await originalJson();
        };

        return response;
    } catch (err) {
        console.error(`[API FETCH EXCEPTION] URL: ${url} | Error:`, err);
        throw err;
    }
};
