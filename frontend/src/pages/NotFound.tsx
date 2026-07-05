import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-4 text-center z-10">
      <h1 className="text-9xl font-bold text-white/5 mb-4">404</h1>
      <h2 className="text-2xl font-semibold text-white mb-2">Room Not Found</h2>
      <p className="text-slate-400 mb-8 max-w-md">
        The room you are looking for does not exist, has expired, or is inactive.
      </p>
      <Link 
        to="/" 
        className="bg-primary hover:bg-secondary text-white font-medium rounded-lg px-6 py-3 transition-colors"
      >
        Go Home
      </Link>
    </div>
  );
}
