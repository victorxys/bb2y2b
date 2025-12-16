import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout/Layout';
import { SpacesList } from './components/spaces/SpacesList';
import { VideosList } from './components/videos/VideosList';
import { DownloadManager } from './components/downloads/DownloadManager';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  const [currentPage, setCurrentPage] = useState<string>('spaces');

  const renderPage = () => {
    switch (currentPage) {
      case 'spaces':
        return <SpacesList />;
      case 'videos':
        return <VideosList />;
      case 'downloads':
        return <DownloadManager />;
      default:
        return <SpacesList />;
    }
  };

  return (
    <QueryClientProvider client={queryClient}>
      <Layout currentPage={currentPage} onNavigate={setCurrentPage}>
        {renderPage()}
      </Layout>
    </QueryClientProvider>
  );
}

export default App;
