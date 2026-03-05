import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'
import LoginModal from './LoginModal'
import RegisterModal from './RegisterModal'

export default function Navbar() {
  const { user, logout } = useAuth()
  const { cart } = useCart()
  const navigate = useNavigate()
  const location = useLocation()
  const [showLogin, setShowLogin] = useState(false)
  const [showRegister, setShowRegister] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <>
      <div className="sticky top-0 z-50 w-full bg-[#141414] border-b-4 border-[#333] relative" style={{ maxWidth: '100%', margin: '0 auto' }}>
        <nav className="max-w-7xl mx-auto px-4 md:px-8 flex justify-between items-center py-3 md:py-4" style={{ maxWidth: '1280px', margin: '0 auto' }}>
          <Link to="/" className="flex items-center gap-2 text-xl font-bold">
            <span className="text-[#ff6b35] text-2xl">◼</span>
            <span>FOODBOX</span>
          </Link>
          
          <button className="md:hidden text-2xl" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? '✕' : '☰'}
          </button>

          <div className={`${mobileMenuOpen ? 'flex' : 'hidden'} md:flex flex-col md:flex-row gap-4 md:gap-8 absolute md:relative top-full left-0 md:left-auto w-full md:w-auto bg-[#141414] md:bg-transparent p-4 md:p-0 border-b-4 md:border-b-0 border-[#333] z-40 md:z-auto`}>
            <Link to="/" className={`font-medium hover:text-[#ff6b35] ${location.pathname === '/' ? 'text-[#ff6b35]' : ''}`}>Home</Link>
            <Link to="/menu" className={`font-medium hover:text-[#ff6b35] ${location.pathname === '/menu' ? 'text-[#ff6b35]' : ''}`}>Menu</Link>
            <Link to="/orders" className={`font-medium hover:text-[#ff6b35] ${location.pathname === '/orders' ? 'text-[#ff6b35]' : ''}`}>Orders</Link>
            <Link to="/subscription" className={`font-medium hover:text-[#ff6b35] ${location.pathname === '/subscription' ? 'text-[#ff6b35]' : ''}`}>Subscribe</Link>
            <Link to="/cart" className="font-medium hover:text-[#ff6b35]">
              Cart <span className="bg-[#ff6b35] text-[#0a0a0a] px-2 py-0.5 text-sm font-bold">{cart.length}</span>
            </Link>
          </div>

          <div className="hidden md:block">
            {user ? (
              <div className="flex gap-4 items-center">
                <span className="text-[#00ff88] font-medium">{user.username}</span>
                <button onClick={handleLogout} className="btn-outline py-2 px-4 text-sm">Logout</button>
              </div>
            ) : (
              <button onClick={() => setShowLogin(true)} className="btn-outline py-2 px-4 text-sm">Login</button>
            )}
          </div>
        </nav>
      </div>

      <div className="md:hidden p-4 bg-[#141414] border-b-4 border-[#333]">
        {user ? (
          <div className="flex justify-between items-center">
            <span className="text-[#00ff88] font-medium">{user.username}</span>
            <button onClick={handleLogout} className="btn-outline py-2 px-4 text-sm">Logout</button>
          </div>
        ) : (
          <button onClick={() => setShowLogin(true)} className="btn-outline w-full py-2">Login</button>
        )}
      </div>

      {showLogin && <LoginModal onClose={() => setShowLogin(false)} onSwitch={() => { setShowLogin(false); setShowRegister(true) }} />}
      {showRegister && <RegisterModal onClose={() => setShowRegister(false)} onSwitch={() => { setShowRegister(false); setShowLogin(true) }} />}
    </>
  )
}
