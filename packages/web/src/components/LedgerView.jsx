import { useState, useEffect } from 'react'
import { ledgerClient } from '../api/ledgerClient'
import LedgerBalance from './LedgerBalance'
import TransactionForm from './TransactionForm'

function LedgerView({ ledgerId }) {
  const [ledger, setLedger] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchLedger = async () => {
    setLoading(true)
    setError(null)

    try {
      const data = await ledgerClient.getLedger(ledgerId)
      setLedger(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (ledgerId) {
      fetchLedger()
    }
  }, [ledgerId])

  const handleTransaction = async () => {
    await fetchLedger()
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8">
        <p className="text-center text-gray-500">Loading ledger...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <LedgerBalance ledgerId={ledger.ledger} balance={ledger.balance} />
      <TransactionForm ledgerId={ledgerId} onTransactionComplete={handleTransaction} />
    </div>
  )
}

export default LedgerView
