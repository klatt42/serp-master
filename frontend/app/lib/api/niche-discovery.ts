import { NicheDiscoveryRequest, NicheDiscoveryResponse } from '@/types/niche';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class NicheDiscoveryAPI {

  static async analyzeNiche(request: NicheDiscoveryRequest): Promise<NicheDiscoveryResponse> {
    const response = await fetch(`${API_BASE_URL}/api/niche/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to analyze niche');
    }

    return response.json();
  }

  static async discoverOpportunities(request: NicheDiscoveryRequest): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/niche/discover`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to discover opportunities');
    }

    return response.json();
  }
}
