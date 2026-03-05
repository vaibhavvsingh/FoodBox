import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="animate-fade-in w-full">
      <section className="w-full min-h-[calc(100vh-180px)] md:min-h-[calc(100vh-140px)] flex items-center py-16 md:py-0">
        <div className="w-full max-w-7xl mx-auto px-4 md:px-8">
          <div className="flex flex-col lg:flex-row gap-8 lg:gap-16 items-center">
            <div className="flex-1 text-center lg:text-left">
              <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold leading-tight mb-4 md:mb-6">
                FUEL YOUR<br />
                <span className="text-[#ff6b35]">FITNESS</span>
              </h1>
              <p className="text-lg md:text-xl text-[#a0a0a0] mb-6 md:mb-8 max-w-xl mx-auto lg:mx-0">
                High protein meals delivered daily. Build muscle while we handle the cooking.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <Link to="/menu" className="btn-primary text-center">View Menu</Link>
                <Link to="/subscription" className="btn-secondary text-center">Get Subscription</Link>
              </div>
            </div>
            <div className="flex-1 flex justify-center lg:justify-end">
              <div className="bg-[#141414] border-4 border-[#333] p-4 md:p-6 lg:p-8 shadow-[6px_6px_0_#333] w-full max-w-sm">
                {[
                  { num: '50g+', label: 'PROTEIN PER MEAL' },
                  { num: '30min', label: 'DELIVERY TIME' },
                  { num: '7days', label: 'FRESH MEALS' }
                ].map((stat, i) => (
                  <div key={i} className="bg-[#1e1e1e] border-2 border-[#ff6b35] p-4 md:p-6 mb-3 last:mb-0 text-center">
                    <span className="block text-3xl md:text-4xl font-bold text-[#ff6b35]">{stat.num}</span>
                    <span className="text-xs text-[#a0a0a0] tracking-wider">{stat.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="w-full py-16 md:py-24">
        <div className="w-full max-w-7xl mx-auto px-4 md:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-8 md:mb-12">WHY FOODBOX?</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8">
            {[
              { icon: '💪', title: 'High Protein', desc: 'Every meal packed with 30-50g of premium protein for muscle growth.' },
              { icon: '⏱️', title: 'Quick Delivery', desc: 'Hot meals delivered within 30 minutes. Track your order in real-time.' },
              { icon: '📦', title: 'Flexible Plans', desc: 'Choose from weekly subscriptions or one-time orders. Cancel anytime.' },
              { icon: '🥗', title: 'Custom Macros', desc: 'Set your protein goals and we\'ll customize your meal plan.' }
            ].map((f, i) => (
              <div key={i} className="card p-6 md:p-8 h-full">
                <div className="text-4xl mb-4 text-center">{f.icon}</div>
                <h3 className="text-xl font-bold mb-2 text-center">{f.title}</h3>
                <p className="text-[#a0a0a0] text-center">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="w-full py-16 md:py-24 text-center bg-[#141414] border-y-4 border-[#333] shadow-[6px_6px_0_#333]">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">START YOUR FITNESS JOURNEY</h2>
          <p className="text-[#a0a0a0] mb-6 md:mb-8">Join thousands who trust FoodBox for their nutrition needs</p>
          <Link to="/subscription" className="btn-primary text-lg px-8 py-4 inline-block">Subscribe Now</Link>
        </div>
      </section>
    </div>
  )
}
