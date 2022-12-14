import { ChakraProvider } from "@chakra-ui/react";
import { QueryClient, QueryClientProvider } from "react-query";
import "./App.css";
import Schedule from "./components/schedule";
import Footer from "./components/footer";
import Navbar from "./components/navbar";

import {
  Outlet,
  RouterProvider,
  createReactRouter,
  createRouteConfig,
  useMatch
} from "@tanstack/react-router";
import PersonComponent from "./components/personComponent";

const rootRoute = createRouteConfig();

const indexRoute = rootRoute.createRoute({
  path: "/",
  component: Schedule
});

const categoryRoute = rootRoute.createRoute({
  path: "$category",
  component: Schedule
});

const personRoute = categoryRoute.createRoute({
  path: "$personId",
  component: PersonComponent
});

const routeConfig = rootRoute.addChildren([indexRoute, categoryRoute.addChildren([personRoute])]);

// Set up a ReactRouter instance
const router = createReactRouter({
  routeConfig,
  defaultPreload: "intent"
});


const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      notifyOnChangeProps: 'tracked',
      refetchOnWindowFocus: false,
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
        <RouterProvider router={router}>
          <div>
            <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
              <Navbar />
              <Outlet /> {/* Start rendering router matches */}
              <div style={{ marginTop: "auto" }}>
                <Footer />
              </div>
            </div>
            <div></div>
          </div>
        </RouterProvider>
      </QueryClientProvider>
    </ChakraProvider>
  );
}

export default App;
