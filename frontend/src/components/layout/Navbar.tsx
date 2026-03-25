import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useCart } from '../../context/CartContext';

export function Navbar() {
  const { isAuthenticated, role, user, logout } = useAuth();
  const { clear } = useCart();

  const handleLogout = () => {
    clear();
    logout();
  };

  return (
    <header className="app-nav">
      <div className="app-shell app-nav__inner">
        <NavLink to="/" className="app-nav__brand">
          Kitchen Manager
        </NavLink>

        <nav className="app-nav__links" aria-label="Main navigation">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `app-nav__link${isActive ? ' app-nav__link--active' : ''}`
            }
          >
            Home
          </NavLink>
          <NavLink
            to="/menu"
            className={({ isActive }) =>
              `app-nav__link${isActive ? ' app-nav__link--active' : ''}`
            }
          >
            Menu
          </NavLink>
          {isAuthenticated && role === 'customer' ? (
            <NavLink
              to="/orders"
              className={({ isActive }) =>
                `app-nav__link${isActive ? ' app-nav__link--active' : ''}`
              }
            >
              Ordini
            </NavLink>
          ) : null}
          {role === 'admin' ? (
            <>
              <NavLink
                to="/admin/menu"
                className={({ isActive }) =>
                  `app-nav__link${isActive ? ' app-nav__link--active' : ''}`
                }
              >
                Gestisci menu
              </NavLink>
              <NavLink
                to="/admin/orders"
                className={({ isActive }) =>
                  `app-nav__link${isActive ? ' app-nav__link--active' : ''}`
                }
              >
                Gestione ordini
              </NavLink>
              <NavLink
                to="/admin/reviews"
                className={({ isActive }) =>
                  `app-nav__link${isActive ? ' app-nav__link--active' : ''}`
                }
              >
                Recensioni
              </NavLink>
            </>
          ) : null}
        </nav>

        <div className="app-nav__actions">
          {isAuthenticated ? (
            <>
              {role === 'admin' ? <span className="role-pill">Area admin</span> : null}
              <span className="user-pill">Ciao, {user?.username ?? 'utente'}</span>
              <button type="button" className="button button--secondary" onClick={handleLogout}>
                Esci
              </button>
            </>
          ) : (
            <NavLink to="/login" className="button button--primary">
              Accedi
            </NavLink>
          )}
        </div>
      </div>
    </header>
  );
}
