export interface ImageProvider {
  generateExpenseItemImage(params: {
    itemLabel: string;
    category?: string;
    description?: string;
  }): Promise<{ imageUrl: string }>;
}

function buildPrompt({
  itemLabel,
  category,
  description
}: {
  itemLabel: string;
  category?: string;
  description?: string;
}) {
  const context = [itemLabel, category, description].filter(Boolean).join(", ");
  return `Photorealistic product-style image of ${context} on a neutral background. No logos, no brand names, no copyrighted characters.`;
}

export class OpenAIImageProvider implements ImageProvider {
  private apiKey: string;

  constructor(apiKey: string | undefined) {
    if (!apiKey) {
      throw new Error("OPENAI_API_KEY is required for image generation.");
    }
    this.apiKey = apiKey;
  }

  async generateExpenseItemImage({
    itemLabel,
    category,
    description
  }: {
    itemLabel: string;
    category?: string;
    description?: string;
  }) {
    const response = await fetch("https://api.openai.com/v1/images/generations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({
        model: "gpt-image-1",
        prompt: buildPrompt({ itemLabel, category, description }),
        size: "1024x1024"
      })
    });

    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(`Image generation failed: ${response.status} ${errorBody}`);
    }

    const payload = (await response.json()) as {
      data?: Array<{ url?: string }>;
    };

    const imageUrl = payload.data?.[0]?.url;
    if (!imageUrl) {
      throw new Error("Image generation response missing url.");
    }

    return { imageUrl };
  }
}

export function getImageProvider() {
  return new OpenAIImageProvider(process.env.OPENAI_API_KEY);
}
