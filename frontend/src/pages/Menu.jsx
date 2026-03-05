import { useState, useEffect } from 'react'
import { useCart } from '../context/CartContext'
import { API } from '../context/AuthContext'

export default function Menu() {
  const [items, setItems] = useState([])
  const [category, setCategory] = useState('all')
  const { addToCart } = useCart()
  const [toast, setToast] = useState(null)

  useEffect(() => {
    loadMenu()
  }, [])

  const loadMenu = async () => {
    try {
      const data = await API.get('/food-items')
      if (Array.isArray(data)) {
        setItems(data)
      } else {
        setItems([])
      }
    } catch (err) {
      setItems([])
    }
  }

  const filtered = category === 'all' ? items : items.filter(i => i.category?.toLowerCase() === category)

  const handleAdd = (item) => {
    addToCart(item)
    setToast(`${item.name} added to cart!`)
    setTimeout(() => setToast(null), 3000)
  }

  const categories = ['all', 'chicken', 'beef', 'fish', 'vegetarian']

  return (
    <div className="animate-fade-in w-full min-h-[calc(100vh-180px)] md:min-h-[calc(100vh-140px)] py-8 md:py-12">
      <div className="w-full max-w-6xl mx-auto px-4 md:px-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-2">OUR <span className="text-[#ff6b35]">MENU</span></h1>
          <p className="text-[#a0a0a0]">High protein meals crafted for your fitness goals</p>
        </div>

        <div className="flex gap-2 md:gap-4 justify-center mb-8 flex-wrap px-2">
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setCategory(cat)}
              className={`px-3 md:px-6 py-2 md:py-3 font-semibold border-[3px] border-[#333] transition-all text-xs md:text-base ${category === cat ? 'bg-[#ff6b35] text-[#0a0a0a]' : 'bg-[#141414] hover:border-[#ff6b35]'}`}
            >
              {cat.charAt(0).toUpperCase() + cat.slice(1)}
            </button>
          ))}
        </div>

        {filtered.length === 0 ? (
          <div className="text-center py-16 text-[#a0a0a0]">
            <p className="text-xl">No menu items available.</p>
            <p className="mt-2">The menu is being loaded from the backend.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
            {filtered.map(item => (
              <div key={item.id} className="card overflow-hidden flex flex-col">
                <div className="h-40 md:h-48 bg-[#1e1e1e] flex items-center justify-center text-5xl md:text-7xl border-b-4 border-[#333] flex-shrink-0">
                  {item.category === 'chicken' ? '🍗' : item.category === 'beef' ? '🥩' : item.category === 'fish' ? '🐟' : '🥗'}
                </div>
                <div className="p-4 md:p-6 flex-1 flex flex-col">
                  <h3 className="text-lg md:text-xl font-bold mb-2">{item.name}</h3>
                  <p className="text-[#a0a0a0] text-sm mb-4 flex-1">{item.description}</p>
                  <div className="flex gap-2 md:gap-4 mb-4">
                    <span className="bg-[#1e1e1e] px-2 md:px-3 py-1 text-xs font-mono">{item.protein_grams}g protein</span>
                    <span className="bg-[#1e1e1e] px-2 md:px-3 py-1 text-xs font-mono">{item.calories} cal</span>
                  </div>
                  <div className="flex justify-between items-center mt-auto">
                    <span className="text-xl md:text-2xl font-bold text-[#ff6b35]">${item.price}</span>
                    <button onClick={() => handleAdd(item)} className="bg-[#ff6b35] text-[#0a0a0a] px-3 md:px-4 py-2 font-semibold border-2 border-[#ff6b35] hover:bg-[#ff8c5a] text-sm md:text-base w-full md:w-auto">
                      Add
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {toast && (
        <div className="toast toast-success">
          {toast}
        </div>
      )}
    </div>
  )
}
