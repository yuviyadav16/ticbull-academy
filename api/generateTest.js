// File: api/generateTest.js
export default async function handler(req, res) {
  // Sirf POST request allow karein
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  // Vercel se aapki secure API Key nikaali ja rahi hai
  const apiKey = process.env.GEMINI_API_KEY;

  if (!apiKey) {
    return res.status(500).json({ error: 'API Key is missing in Vercel Environment Variables' });
  }

  const promptText = req.body.prompt;
  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ parts: [{ text: promptText }] }]
      })
    });

    const data = await response.json();
    
    // Extracting and cleaning the text
    let aiResponseText = data.candidates[0].content.parts[0].text;
    aiResponseText = aiResponseText.replace(/```json/g, '').replace(/```/g, '').trim();
    
    // JSON response wapas frontend ko bhejein
    res.status(200).json(JSON.parse(aiResponseText));

  } catch (error) {
    console.error("Gemini API Error:", error);
    res.status(500).json({ error: 'Failed to generate question from AI' });
  }
}

