const API_BASE = ''; // Empty because Vite proxy handles routing

export class LedgerClient {
  async createLedger() {
    const response = await fetch(`${API_BASE}/ledger/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to create ledger: ${response.statusText}`);
    }

    return response.json();
  }

  async getLedger(ledgerId) {
    const response = await fetch(`${API_BASE}/ledger/${ledgerId}`);

    if (!response.ok) {
      throw new Error(`Failed to get ledger: ${response.statusText}`);
    }

    return response.json();
  }

  async creditLedger(ledgerId, amount) {
    const response = await fetch(`${API_BASE}/ledger/${ledgerId}/credits`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ amount: parseFloat(amount) }),
    });

    if (!response.ok) {
      throw new Error(`Failed to credit ledger: ${response.statusText}`);
    }

    return response.json();
  }

  async debitLedger(ledgerId, amount) {
    const response = await fetch(`${API_BASE}/ledger/${ledgerId}/debits`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ amount: parseFloat(amount) }),
    });

    if (!response.ok) {
      throw new Error(`Failed to debit ledger: ${response.statusText}`);
    }

    return response.json();
  }
}

export const ledgerClient = new LedgerClient();
