const OfflinePage = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <div className="text-center p-8">
      <div className="text-6xl mb-4">📡</div>
      <h1 className="text-2xl font-bold text-gray-800 mb-2">You're Offline</h1>
      <p className="text-gray-600 mb-6">
        Please check your internet connection and try again.
      </p>
      <button
        onClick={() => window.location.reload()}
        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
      >
        Retry
      </button>
    </div>
  </div>
);

export default OfflinePage;
