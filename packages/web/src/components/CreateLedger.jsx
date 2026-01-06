import { useState } from 'react'
import { ledgerClient } from '../api/ledgerClient'

function CreateLedger({ onLedgerCreated }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleCreate = async () => {
    setLoading(true)
    setError(null)

    try {
      const result = await ledgerClient.createLedger()
      onLedgerCreated(result.ledger_id)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Create Ledger</h2>

      <p className="text-gray-600 mb-6">
        Create a new ledger with an initial balance of $500.00
      </p>

      <button
        onClick={handleCreate}
        disabled={loading}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {loading ? 'Creating...' : 'Create New Ledger'}
      </button>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}
    </div>
  )
}

export default CreateLedger
