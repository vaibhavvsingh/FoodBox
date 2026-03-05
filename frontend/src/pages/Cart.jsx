import { useState } from 'react'
import { useCart } from '../context/CartContext'
import { useAuth, API } from '../context/AuthContext'

export default function Cart() {
  const { cart, removeFromCart, updateQuantity, total, clearCart } = useCart()
  const { user, token } = useAuth()
  const [showCheckout, setShowCheckout] = useState(false)
  const [address, setAddress] = useState(user?.address || '')
  const [notes, setNotes] = useState('')
  const [paymentMethod, setPaymentMethod] = useState('card')
  const [toast, setToast] = useState(null)

  const handleCheckout = async (e) => {
    e.preventDefault()
    if (!token) {
      setToast('Please login to checkout')
      setTimeout(() => setToast(null), 3000)
      return
    }

    const orderData = {
      delivery_address: address,
      notes,
      items: cart.map(item => ({ food_item_id: item.id, quantity: item.quantity }))
    }

    try {
      const order = await API.post('/orders', orderData, token)
      await API.post('/payments', { order_id: order.id, amount: total, payment_method: paymentMethod }, token)
      clearCart()
      setShowCheckout(false)
      setToast('Order placed successfully!')
    } catch (err) {
      setToast(err.message)
    }
    setTimeout(() => setToast(null), 3000)
  }

  return (
    <div className="animate-fade-in w-full min-h-[calc(100vh-180px)] md:min-h-[calc(100vh-140px)] py-8 md:py-12">
      <div className="w-full max-w-6xl mx-auto px-4 md:px-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-2">YOUR <span className="text-[#ff6b35]">CART</span></h1>
          <p className="text-[#a0a0a0]">Review and checkout your order</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8">
          <div className="lg:col-span-2">
            <div className="card p-4 md:p-6">
              {cart.length === 0 ? (
                <div className="text-center py-12 text-[#a0a0a0]">
                  <p>Your cart is empty</p>
                </div>
              ) : (
                cart.map(item => (
                  <div key={item.id} className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 py-4 border-b-2 border-[#333] last:border-0">
                    <div className="flex-1">
                      <h4 className="font-bold">{item.name}</h4>
                      <span className="text-[#a0a0a0]">${item.price}</span>
                    </div>
                    <div className="flex items-center gap-2 md:gap-4 w-full sm:w-auto justify-between sm:justify-end">
                      <div className="flex items-center gap-1 md:gap-2">
                        <button onClick={() => updateQuantity(item.id, item.quantity - 1)} className="w-9 h-9 md:w-8 md:h-8 bg-[#1e1e1e] border-2 border-[#333] font-bold hover:border-[#ff6b35] flex items-center justify-center text-lg md:text-base">-</button>
                        <span className="font-mono w-8 md:w-8 text-center">{item.quantity}</span>
                        <button onClick={() => updateQuantity(item.id, item.quantity + 1)} className="w-9 h-9 md:w-8 md:h-8 bg-[#1e1e1e] border-2 border-[#333] font-bold hover:border-[#ff6b35] flex items-center justify-center text-lg md:text-base">+</button>
                      </div>
                      <button onClick={() => removeFromCart(item.id)} className="text-red-500 text-xl ml-2 bg-transparent border-0 cursor-pointer">×</button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div>
            <div className="card p-4 md:p-6 lg:sticky lg:top-24">
              <h3 className="text-xl font-bold mb-4">Order Summary</h3>
              <div className="space-y-2 mb-4">
                <div className="flex justify-between">
                  <span>Subtotal</span>
                  <span>${total.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Delivery</span>
                  <span className="text-[#00ff88]">FREE</span>
                </div>
                <div className="flex justify-between pt-2 border-t-2 border-[#333] font-bold text-lg">
                  <span>Total</span>
                  <span className="text-[#ff6b35]">${total.toFixed(2)}</span>
                </div>
              </div>
              <button
                onClick={() => setShowCheckout(true)}
                disabled={cart.length === 0}
                className="btn-primary w-full disabled:opacity-50"
              >
                Checkout
              </button>
            </div>
          </div>
        </div>
      </div>

      {showCheckout && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-[100] p-4 overflow-y-auto" onClick={() => setShowCheckout(false)}>
          <div className="bg-[#141414] border-4 border-[#333] p-4 md:p-8 w-full max-w-md shadow-[6px_6px_0_#333] relative my-8" onClick={e => e.stopPropagation()}>
            <button onClick={() => setShowCheckout(false)} className="absolute top-3 right-3 md:top-4 md:right-4 text-2xl hover:text-[#ff6b35] bg-transparent border-0 cursor-pointer">&times;</button>
            <h2 className="text-2xl font-bold mb-6 text-center">Checkout</h2>
            <form onSubmit={handleCheckout} className="space-y-4">
              <div>
                <label className="block font-medium mb-2">Delivery Address</label>
                <textarea value={address} onChange={e => setAddress(e.target.value)} className="input-field w-full h-24" required />
              </div>
              <div>
                <label className="block font-medium mb-2">Order Notes</label>
                <textarea value={notes} onChange={e => setNotes(e.target.value)} className="input-field w-full h-20" />
              </div>
              <div>
                <label className="block font-medium mb-2">Payment Method</label>
                <select value={paymentMethod} onChange={e => setPaymentMethod(e.target.value)} className="input-field w-full">
                  <option value="card">Credit Card</option>
                  <option value="cash">Cash on Delivery</option>
                </select>
              </div>
              <button type="submit" className="btn-primary w-full text-lg py-3">Place Order</button>
            </form>
          </div>
        </div>
      )}

      {toast && (
        <div className={`toast ${toast.includes('success') ? 'toast-success' : 'toast-error'}`}>
          {toast}
        </div>
      )}
    </div>
  )
}
