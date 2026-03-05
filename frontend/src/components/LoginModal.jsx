import { useState } from 'react'
import { useAuth } from '../context/AuthContext'

export default function LoginModal({ onClose, onSwitch }) {
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await login(username, password)
      onClose()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-[100] p-4 overflow-y-auto">
      <div className="bg-[#141414] border-4 border-[#333] p-4 md:p-8 w-full max-w-md shadow-[6px_6px_0_#333] relative my-8" onClick={e => e.stopPropagation()}>
        <button onClick={onClose} className="absolute top-3 right-3 md:top-4 md:right-4 text-2xl hover:text-[#ff6b35] bg-transparent border-0 cursor-pointer">&times;</button>
        <h2 className="text-2xl font-bold mb-6 text-center">Welcome Back</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <p className="text-red-500 text-sm text-center">{error}</p>}
          <div>
            <label className="block font-medium mb-2">Username</label>
            <input type="text" value={username} onChange={e => setUsername(e.target.value)} className="input-field w-full" required />
          </div>
          <div>
            <label className="block font-medium mb-2">Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} className="input-field w-full" required />
          </div>
          <button type="submit" className="btn-primary w-full">Login</button>
        </form>
        <p className="mt-4 text-center text-[#a0a0a0]">
          Don't have an account? <button onClick={onSwitch} className="text-[#ff6b35] font-medium bg-transparent border-0 cursor-pointer">Register</button>
        </p>
      </div>
    </div>
  )
}
