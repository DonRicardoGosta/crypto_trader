import { Route, Routes } from "react-router-dom";
import Layout from "./Layout";
import HistoryPage from "./pages/HistoryPage";
import LivePage from "./pages/LivePage";
import SettingsPage from "./pages/SettingsPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<LivePage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="history" element={<HistoryPage />} />
      </Route>
    </Routes>
  );
}
