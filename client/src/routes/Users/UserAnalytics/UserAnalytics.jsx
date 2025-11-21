import styles from "./UserAnalytics.module.css";
import React, { useEffect, useState } from "react";
import { useAuth } from "../../../context/AuthContext";
import toast from "react-hot-toast";
import { formatDate } from "../../../utils/Helpers";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ComposedChart,
} from "recharts";

const UserAnalytics = () => {
  const { user } = useAuth();
  const today = new Date().toLocaleDateString("en-CA");
  const [users, setUsers] = useState([]);
  const [userID, setUserID] = useState(user.id);
  const [dates, setDates] = useState({
    start_date: "2025-11-01",
    end_date: "2025-11-19",
  });

  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchUsers = async () => {
      const response = await fetch("/api/read/get_users");
      const data = await response.json();
      if (!data.success) {
        toast.error(data.message);
        return;
      }
      setUsers(data.users);
    };
    fetchUsers();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch(
        `/api/analytics/user_analytics/${userID}?start_date=${dates.start_date}&end_date=${dates.end_date}`
      );
      const data = await response.json();
      setData(data.data);
    };
    fetchData();
  }, [userID]);

  const shiftDate = (dateStr, amount) => {
    const d = new Date(dateStr + "T00:00");
    d.setDate(d.getDate() + amount);
    return d.toLocaleDateString("en-CA");
  };

  return (
    <div className={styles.userAnalyticsContainer}>
      <div className={styles.analyticsSelectionBar}>
        <select
          name="user_id"
          value={userID}
          onChange={(e) => setUserID(e.target.value)}
        >
          <option value="">--Select User--</option>
          {users.map(({ id, first_name, last_name }) => (
            <option value={id} key={id}>
              {first_name} {last_name}
            </option>
          ))}
        </select>
      </div>
      {data && (
        <div className={styles.analyticsData}>
          {/* 1️⃣ Line Chart for Subtotal and Units */}
          <h3>Revenue vs Units Over Time</h3>
          <ResponsiveContainer width="100%" height={200}>
            <ComposedChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis
                yAxisId="left"
                label={{ value: "Revenue", angle: -90, position: "insideLeft" }}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                label={{ value: "Units", angle: 90, position: "insideRight" }}
              />
              <Tooltip />
              <Legend />
              <Bar
                yAxisId="left"
                dataKey="sub_total"
                fill="#8884d8"
                name="Sub Total"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="units"
                stroke="#82ca9d"
                name="Units Sold"
              />
            </ComposedChart>
          </ResponsiveContainer>

          {/* 2️⃣ Stacked Bar Chart for Revenue Categories */}
          <h3>Revenue Breakdown</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart
              data={data}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="new" stackId="revenue" fill="#8884d8" />
              <Bar dataKey="used" stackId="revenue" fill="#82ca9d" />
              <Bar
                dataKey="extended_warranty"
                stackId="revenue"
                fill="#ffc658"
              />
              <Bar dataKey="diagnostic_fees" stackId="revenue" fill="#d0ed57" />
              <Bar dataKey="in_shop_repairs" stackId="revenue" fill="#a4de6c" />
              <Bar dataKey="ebay_sales" stackId="revenue" fill="#8dd1e1" />
              <Bar dataKey="service" stackId="revenue" fill="#83a6ed" />
              <Bar dataKey="parts" stackId="revenue" fill="#8884d8" />
              <Bar dataKey="delivery" stackId="revenue" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>

          {/* 3️⃣ Stacked Bar Chart for Payment Methods */}
          <h3>Payment Methods</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart
              data={data}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="cash" stackId="payments" fill="#8884d8" />
              <Bar dataKey="card" stackId="payments" fill="#82ca9d" />
              <Bar dataKey="checks" stackId="payments" fill="#ffc658" />
              <Bar dataKey="acima" stackId="payments" fill="#d0ed57" />
              <Bar dataKey="tower_loan" stackId="payments" fill="#a4de6c" />
            </BarChart>
          </ResponsiveContainer>

          {/* 4️⃣ Line Chart for Deductions */}
          <h3>Deductions Over Time</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="deductions"
                stroke="#ff7300"
                name="Deductions"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default UserAnalytics;
