import { useState, useEffect } from 'react'
import { useAuth, API } from '../context/AuthContext'

export default function Subscription() {
  const { token } = useAuth()
  const [subscription, setSubscription] = useState(null)
  const [toast, setToast] = useState(null)

  useEffect(() => {
    if (token) loadSubscription()
  }, [token])

  const loadSubscription = async () => {
    try {
      const data = await API.get('/subscriptions/me', token)
      setSubscription(data)
    } catch (err) {
      setSubscription(null)
    }
  }

  const handleSubscribe = async (plan) => {
    if (!token) {
      setToast('Please login to subscribe')
      setTimeout(() => setToast(null), 3000)
      return
    }

    const plans = {
      basic: { plan: 'basic', meals_per_week: 7, protein_target_grams: 150 },
      premium: { plan: 'premium', meals_per_week: 7, protein_target_grams: 200 },
      family: { plan: 'family', meals_per_week: 14, protein_target_grams: 250 }
    }

    try {
      await API.post('/subscriptions', plans[plan], token)
      setToast('Subscription activated!')
      loadSubscription()
    } catch (err) {
      setToast(err.message)
    }
    setTimeout(() => setToast(null), 3000)
  }

  const plansList = [
    { name: 'BASIC', price: 99, badge: 'STARTER', plan: 'basic', features: ['7 meals per week', '150g protein target', 'Free delivery', 'Standard menu access'] },
    { name: 'PREMIUM', price: 149, badge: 'MOST POPULAR', plan: 'premium', featured: true, features: ['7 meals per week', '200g protein target', 'Priority delivery', 'Premium menu access', 'Custom macro adjustments'] },
    { name: 'FAMILY', price: 249, badge: 'FAMILY SIZE', plan: 'family', features: ['14 meals per week', '250g protein target', 'Priority delivery', 'Full menu access', 'Family portions'] }
  ]

  return (
    <div className="animate-fade-in w-full min-h-[calc(100vh-180px)] md:min-h-[calc(100vh-140px)] py-8 md:py-12">
      <div className="w-full max-w-6xl mx-auto px-4 md:px-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-2">SUBSCRIPTION <span className="text-[#ff6b35]">PLANS</span></h1>
          <p className="text-[#a0a0a0]">Choose the plan that fits your goals</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8 mb-12">
          {plansList.map(p => (
            <div key={p.name} className={`card p-6 md:p-8 ${p.featured ? 'border-[#ff6b35] relative' : ''} flex flex-col`}>
              {p.featured && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[#ff6b35] text-[#0a0a0a] px-3 py-1 text-xs font-bold whitespace-nowrap">
                  MOST POPULAR
                </span>
              )}
              <div className="flex flex-col items-center mb-6">
                <h3 className="text-2xl font-bold mb-2">{p.name}</h3>
                <span className="bg-[#1e1e1e] px-3 py-1 text-xs">{p.badge}</span>
              </div>
              <div className="text-center mb-6">
                <span className="text-4xl md:text-5xl font-bold text-[#ff6b35]">${p.price}</span>
                <span className="text-[#a0a0a0]">/month</span>
              </div>
              <ul className="space-y-2 mb-8 flex-1">
                {p.features.map((f, i) => (
                  <li key={i} className="text-[#a0a0a0] text-center md:text-left">→ {f}</li>
                ))}
              </ul>
              <button onClick={() => handleSubscribe(p.plan)} className="btn-primary w-full mt-auto">
                Select Plan
              </button>
            </div>
          ))}
        </div>

        {subscription && (
          <div className="card p-6 md:p-8 max-w-xl mx-auto">
            <h3 className="text-2xl font-bold mb-4 text-center">Your Active Subscription</h3>
            <div className="space-y-2">
              <p><span className="text-[#a0a0a0]">Plan:</span> {subscription.plan}</p>
              <p><span className="text-[#a0a0a0]">Price:</span> ${subscription.monthly_price}/month</p>
              <p><span className="text-[#a0a0a0]">Meals/week:</span> {subscription.meals_per_week}</p>
              <p><span className="text-[#a0a0a0]">Protein target:</span> {subscription.protein_target_grams}g</p>
              <p><span className="text-[#a0a0a0]">Status:</span> {subscription.is_active ? 'Active' : 'Inactive'}</p>
            </div>
          </div>
        )}
      </div>

      {toast && (
        <div className={`toast ${toast.includes('activated') ? 'toast-success' : 'toast-error'}`}>
          {toast}
        </div>
      )}
    </div>
  )
}
