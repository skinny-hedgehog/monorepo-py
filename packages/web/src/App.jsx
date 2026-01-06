import { useState } from 'react'
import CreateLedger from './components/CreateLedger'
import LedgerView from './components/LedgerView'

function App() {
  const [currentLedgerId, setCurrentLedgerId] = useState(null)

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-blue-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold">Skinny Hedgehog Ledger</h1>
          <p className="text-blue-100 mt-2">Event-Sourced Ledger Management System</p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <CreateLedger onLedgerCreated={setCurrentLedgerId} />
          </div>

          <div className="lg:col-span-2">
            {currentLedgerId ? (
              <LedgerView ledgerId={currentLedgerId} />
            ) : (
              <div className="bg-white rounded-lg shadow-md p-8 text-center text-gray-500">
                <p className="text-lg">Create a new ledger to get started</p>
              </div>
            )}
          </div>
        </div>
      </main>

      <footer className="mt-16 bg-gray-800 text-white py-6">
        <div className="container mx-auto px-4 text-center">
          <p className="text-gray-400">
            Built with React, Tailwind CSS, and FastAPI
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
