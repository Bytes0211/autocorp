export default function ChatHeader() {
  return (
    <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-4 shadow-lg">
      <div className="flex items-center space-x-3">
        <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center text-blue-600 font-bold text-xl shadow-md">
          M
        </div>
        <div>
          <h1 className="text-xl font-bold">Mici</h1>
          <p className="text-sm text-blue-100">
            AutoCorp AI Assistant
          </p>
        </div>
      </div>
    </div>
  );
}
