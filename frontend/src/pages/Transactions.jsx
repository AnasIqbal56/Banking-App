import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../services/api'

const Transactions = () => {
  const { accountId } = useParams()
  const [account, setAccount] = useState(null)
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [accountRes, transactionsRes] = await Promise.all([
          api.get(`/api/accounts/${accountId}`),
          api.get(`/api/transactions/${accountId}`)
        ])
        setAccount(accountRes.data)
        setTransactions(transactionsRes.data)
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [accountId])

  const getTransactionIcon = (type) => {
    switch (type) {
      case 'deposit':
        return '↓'
      case 'withdrawal':
        return '↑'
      case 'transfer':
        return '↔'
      case 'bill_payment':
        return '📄'
      default:
        return '•'
    }
  }

  const getTransactionColor = (type) => {
    switch (type) {
      case 'deposit':
        return 'text-green-600'
      case 'withdrawal':
      case 'bill_payment':
        return 'text-red-600'
      case 'transfer':
        return 'text-blue-600'
      default:
        return 'text-gray-600'
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!account) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Account not found</p>
        <Link to="/accounts" className="text-primary-600 hover:underline mt-2 inline-block">
          Back to Accounts
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link
          to="/accounts"
          className="text-gray-500 hover:text-gray-700"
        >
          ← Back
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Transaction History</h1>
      </div>

      {/* Account summary */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{account.account_name}</h2>
            <p className="text-sm text-gray-500">Account: {account.account_number}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Current Balance</p>
            <p className="text-2xl font-bold text-gray-900">
              ${account.balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </p>
          </div>
        </div>
      </div>

      {/* Transactions list */}
      <div className="bg-white rounded-xl shadow-sm">
        <div className="p-6 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">Recent Transactions</h2>
        </div>

        {transactions.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-gray-500">No transactions yet</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {transactions.map((transaction) => (
              <div key={transaction.id} className="p-4 hover:bg-gray-50">
                <div className="flex justify-between items-start">
                  <div className="flex items-start gap-3">
                    <span className={`text-2xl ${getTransactionColor(transaction.transaction_type)}`}>
                      {getTransactionIcon(transaction.transaction_type)}
                    </span>
                    <div>
                      <p className="font-medium text-gray-900">
                        {transaction.description || transaction.transaction_type.replace('_', ' ')}
                      </p>
                      <p className="text-sm text-gray-500 capitalize">
                        {transaction.transaction_type.replace('_', ' ')}
                        {transaction.recipient_account && (
                          <span> • To: {transaction.recipient_account}</span>
                        )}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        {new Date(transaction.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`font-semibold ${
                      transaction.transaction_type === 'deposit' 
                        ? 'text-green-600' 
                        : 'text-red-600'
                    }`}>
                      {transaction.transaction_type === 'deposit' ? '+' : '-'}
                      ${transaction.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </p>
                    <p className="text-sm text-gray-500">
                      Balance: ${transaction.balance_after.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Transactions
