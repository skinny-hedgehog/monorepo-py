function LedgerBalance({ ledgerId, balance }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Ledger Balance</h2>

      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Ledger ID:</span>
          <span className="font-mono text-sm text-gray-800">{ledgerId}</span>
        </div>

        <div className="flex justify-between items-center pt-3 border-t border-gray-200">
          <span className="text-gray-600 font-semibold">Current Balance:</span>
          <span className="text-3xl font-bold text-green-600">
            ${parseFloat(balance).toFixed(2)}
          </span>
        </div>
      </div>
    </div>
  )
}

export default LedgerBalance
