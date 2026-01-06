import { useState } from 'react'
import { ledgerClient } from '../api/ledgerClient'

function TransactionForm({ ledgerId, onTransactionComplete }) {
  const [amount, setAmount] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  const handleTransaction = async (type) => {
    if (!amount || parseFloat(amount) <= 0) {
      setError('Please enter a valid amount')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      if (type === 'credit') {
        await ledgerClient.creditLedger(ledgerId, amount)
        setSuccess(`Successfully credited $${amount}`)
      } else {
        await ledgerClient.debitLedger(ledgerId, amount)
        setSuccess(`Successfully debited $${amount}`)
      }

      setAmount('')
      onTransactionComplete()

      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Add Transaction</h2>

      <div className="space-y-4">
        <div>
          <label htmlFor="amount" className="block text-gray-700 font-semibold mb-2">
            Amount
          </label>
          <input
            id="amount"
            type="number"
            step="0.01"
            min="0"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0.00"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => handleTransaction('credit')}
            disabled={loading}
            className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? 'Processing...' : 'Credit'}
          </button>

          <button
            onClick={() => handleTransaction('debit')}
            disabled={loading}
            className="bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? 'Processing...' : 'Debit'}
          </button>
        </div>

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {success && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-800 text-sm">{success}</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default TransactionForm
