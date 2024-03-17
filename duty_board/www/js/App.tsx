import { ChakraProvider } from "@chakra-ui/react";
import {QueryCache, QueryClient, QueryClientProvider} from "@tanstack/react-query";
import "./App.css";
import Schedule from "./components/schedule";
import Footer from "./components/footer";
import Navbar from "./components/navbar";

import {
  Outlet,
  RouterProvider,
  createRouter,
  createRoute,
  createRootRoute,
} from "@tanstack/react-router";
import AnnouncementBar from "./components/announcementBar";
import SingleCalendar from "./components/singleCalendar";
import useErrorToast from "./utils/useErrorToast";

const rootRoute = createRootRoute({
  component: () => (
    <div>
      <div style={{minHeight: "100vh", display: "flex", flexDirection: "column"}}>
        <AnnouncementBar/>
        <Navbar/>
        <main>
          <Outlet/> {/* Start rendering router matches */}
        </main>
        <div style={{marginTop: "auto"}}>
          <Footer/>
        </div>
      </div>
      <div></div>
    </div>
  )
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: Schedule
});

const categoryRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "$category",
  component: Schedule
});

const calendarRoute = createRoute({
  getParentRoute: () => categoryRoute,
  path: "$calendarId",
  component: SingleCalendar
});


const routeTree = rootRoute.addChildren([indexRoute, categoryRoute.addChildren([calendarRoute])]);

// Set up a ReactRouter instance
const router = createRouter({routeTree, defaultPreload: "intent"});

const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: (error, query) => {

      useErrorToast()({error});
    },
  }),
  defaultOptions: {
    queries: {
      notifyOnChangeProps: 'all',
      refetchOnWindowFocus: true,
      retry: 1,
      retryDelay: 500,
      refetchOnMount: true, // Refetches stale queries, not "always"
      staleTime: 5 * 60 * 1000, // 5 minutes
      initialDataUpdatedAt: new Date().setMinutes(-6), // make sure initial data is already expired
    },
    mutations: {
      retry: 1,
      retryDelay: 500,
    },
  },
});

function App() {
  return (
    <ChakraProvider>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </ChakraProvider>
  );
}

export default App;
