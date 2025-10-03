export async function sendMessage(userMessage) {
  const response = await fetch(import.meta.env.VITE_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": import.meta.env.VITE_API_KEY,
    },
    body: JSON.stringify({ text: userMessage }),
  });

  if (!response.ok) {
    throw new Error("Error contacting server");
  }

  return response.json();
}
