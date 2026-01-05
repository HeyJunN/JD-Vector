import { Link } from 'react-router-dom';

export const Header = () => {
  return (
    <header className="sticky top-0 z-50 h-14 border-b border-slate-800/50 bg-slate-900/80 backdrop-blur-md">
      <div className="mx-auto flex h-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo */}
        <Link to="/" className="group flex items-center space-x-3">
          <img
            src="/assets/favicon.svg"
            alt="JD-Vector Logo"
            className="h-7 w-7 transition-transform group-hover:scale-110"
          />
          <span className="text-lg font-bold tracking-tight text-slate-50 transition-colors group-hover:text-white">
            JD-Vector
          </span>
        </Link>

        {/* Right side - Reserved for future nav/profile */}
        <div className="flex items-center space-x-4">
          {/* TODO: Add navigation or user profile */}
        </div>
      </div>
    </header>
  );
};

export default Header;
