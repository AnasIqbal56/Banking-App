import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'

const Dashboard = () => {
  const { user } = useAuth()
  const [accounts, setAccounts] = useState([])
  const [bills, setBills] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [accountsRes, billsRes] = await Promise.all([
          api.get('/api/accounts'),
          api.get('/api/bills')
        ])
        setAccounts(accountsRes.data)
        setBills(billsRes.data.filter(b => b.status !== 'paid').slice(0, 3))
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const totalBalance = accounts.reduce((sum, acc) => sum + acc.balance, 0)
  const pendingBills = bills.reduce((sum, bill) => sum + bill.amount, 0)

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Welcome section */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.full_name?.split(' ')[0]}!
        </h1>
        <p className="text-gray-600 mt-1">Here's your financial overview</p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <p className="text-sm text-gray-500 uppercase tracking-wide">Total Balance</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            ${totalBalance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Across {accounts.length} account{accounts.length !== 1 ? 's' : ''}
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <p className="text-sm text-gray-500 uppercase tracking-wide">Pending Bills</p>
          <p className="text-3xl font-bold text-orange-600 mt-2">
            ${pendingBills.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </p>
          <p className="text-sm text-gray-500 mt-2">
            {bills.length} bill{bills.length !== 1 ? 's' : ''} due
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <p className="text-sm text-gray-500 uppercase tracking-wide">Quick Actions</p>
          <div className="mt-4 space-y-2">
            <Link
              to="/accounts"
              className="block text-primary-600 hover:text-primary-700 font-medium"
            >
              → View Accounts
            </Link>
            <Link
              to="/bills"
              className="block text-primary-600 hover:text-primary-700 font-medium"
            >
              → Pay Bills
            </Link>
          </div>
        </div>
      </div>

      {/* Accounts section */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-semibold text-gray-900">Your Accounts</h2>
          <Link
            to="/accounts"
            className="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            View all →
          </Link>
        </div>

        {accounts.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500">No accounts yet</p>
            <Link
              to="/accounts"
              className="mt-2 inline-block text-primary-600 hover:text-primary-700 font-medium"
            >
              Create your first account
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {accounts.slice(0, 3).map((account) => (
              <div
                key={account.id}
                className="flex justify-between items-center p-4 bg-gray-50 rounded-lg"
              >
                <div>
                  <p className="font-medium text-gray-900">{account.account_name}</p>
                  <p className="text-sm text-gray-500">****{account.account_number.slice(-4)}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900">
                    ${account.balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </p>
                  <Link
                    to={`/transactions/${account.id}`}
                    className="text-sm text-primary-600 hover:text-primary-700"
                  >
                    View transactions
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Upcoming bills */}
      {bills.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Upcoming Bills</h2>
            <Link
              to="/bills"
              className="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              View all →
            </Link>
          </div>

          <div className="space-y-4">
            {bills.map((bill) => (
              <div
                key={bill.id}
                className="flex justify-between items-center p-4 bg-gray-50 rounded-lg"
              >
                <div>
                  <p className="font-medium text-gray-900">{bill.provider_name}</p>
                  <p className="text-sm text-gray-500 capitalize">{bill.bill_type}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900">
                    ${bill.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </p>
                  <p className={`text-sm ${bill.status === 'overdue' ? 'text-red-600' : 'text-gray-500'}`}>
                    Due: {new Date(bill.due_date).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
