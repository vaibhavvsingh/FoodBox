import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth, API } from '../context/AuthContext'

export default function Orders() {
  const { token } = useAuth()
  const [orders, setOrders] = useState([])

  useEffect(() => {
    if (token) loadOrders()
  }, [token])

  const loadOrders = async () => {
    try {
      const data = await API.get('/orders', token)
      setOrders(data)
    } catch (err) {
      console.error(err)
    }
  }

  const statusColors = {
    pending: 'bg-yellow-400 text-black',
    preparing: 'bg-green-500 text-black',
    out_for_delivery: 'bg-blue-500 text-white',
    delivered: 'bg-[#00ff88] text-black',
  }

  return (
    <div className="animate-fade-in w-full min-h-[calc(100vh-180px)] md:min-h-[calc(100vh-140px)] py-8 md:py-12">
      <div className="w-full max-w-4xl mx-auto px-4 md:px-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-2">YOUR <span className="text-[#ff6b35]">ORDERS</span></h1>
          <p className="text-[#a0a0a0]">Track and manage your orders</p>
        </div>

        {!token ? (
          <div className="text-center py-16">
            <p className="text-[#a0a0a0]">Please login to view your orders.</p>
          </div>
        ) : orders.length === 0 ? (
          <div className="text-center py-16 text-[#a0a0a0]">
            <p>No orders yet. <Link to="/menu" className="text-[#ff6b35]">Browse our menu</Link></p>
          </div>
        ) : (
          <div className="space-y-4 md:space-y-6">
            {orders.map(order => (
              <div key={order.id} className="card p-4 md:p-6">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b-2 border-[#333] pb-3 md:pb-4 mb-3 md:mb-4">
                  <span className="font-mono font-bold">Order #{order.id}</span>
                  <span className={`px-3 py-1 text-sm font-semibold uppercase ${statusColors[order.status] || 'bg-gray-500'}`}>
                    {order.status}
                  </span>
                </div>
                <div className="space-y-2 mb-4">
                  {order.items?.map((item, i) => (
                    <div key={i} className="flex justify-between text-[#a0a0a0] text-sm md:text-base">
                      <span>{item.quantity}x Item #{item.food_item_id}</span>
                      <span>${item.subtotal}</span>
                    </div>
                  ))}
                </div>
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 pt-3 md:pt-4 border-t-2 border-[#333]">
                  <span className="text-lg md:text-xl font-bold">${order.total_amount}</span>
                  <span className="text-[#a0a0a0] text-sm">{new Date(order.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
