import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-indigo-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold">
              🔍 Deepfake Detector
            </Link>
          </div>

          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <Link
                  to="/dashboard"
                  className="hover:bg-indigo-700 px-3 py-2 rounded-md"
                >
                  Dashboard
                </Link>
                <Link
                  to="/analysis"
                  className="hover:bg-indigo-700 px-3 py-2 rounded-md"
                >
                  Analyze
                </Link>
                <Link
                  to="/history"
                  className="hover:bg-indigo-700 px-3 py-2 rounded-md"
                >
                  History
                </Link>
                {isAdmin && (
                  <Link
                    to="/admin"
                    className="hover:bg-indigo-700 px-3 py-2 rounded-md"
                  >
                    Admin
                  </Link>
                )}
                <div className="flex items-center space-x-2">
                  <span className="text-sm">👤 {user.username}</span>
                  <button
                    onClick={handleLogout}
                    className="bg-red-500 hover:bg-red-600 px-4 py-2 rounded-md"
                  >
                    Logout
                  </button>
                </div>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="hover:bg-indigo-700 px-3 py-2 rounded-md"
                >
                  Login
                </Link>
                <Link
                  to="/signup"
                  className="bg-white text-indigo-600 hover:bg-gray-100 px-4 py-2 rounded-md font-semibold"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;