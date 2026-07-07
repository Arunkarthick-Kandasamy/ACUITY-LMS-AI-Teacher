import { useState, useEffect } from 'react';
import { apiRequest } from '../services/api';

interface Plan {
  id: string;
  name: string;
  description: string | null;
  price_monthly: number;
  price_yearly: number;
  currency: string;
  max_students: number;
  features: string | null;
}

interface Subscription {
  plan_name: string;
  status: string;
  billing_cycle: string;
  current_period_end: string | null;
}

const SubscriptionPage = () => {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [sub, setSub] = useState<Subscription | null>(null);

  useEffect(() => {
    apiRequest('/payments/plans').then((res: any) => setPlans(Array.isArray(res?.data) ? res.data : [])).catch(() => {});
    apiRequest('/payments/subscription').then((res: any) => setSub(res?.data || null)).catch(() => {});
  }, []);

  const subscribe = async (planId: string, billingCycle: string) => {
    await apiRequest('/payments/subscribe', { method: 'POST', body: JSON.stringify({ plan_id: planId, billing_cycle: billingCycle }) });
    const res: any = await apiRequest('/payments/subscription');
    setSub(res?.data || null);
  };

  const cancel = async () => {
    await apiRequest('/payments/cancel', { method: 'POST' });
    setSub(null);
  };

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Subscription</h1>
      {sub ? (
        <div className="bg-white p-6 rounded-lg border mb-6">
          <h2 className="text-lg font-semibold">{sub.plan_name}</h2>
          <p className="text-sm text-gray-500 mt-1">Status: <span className="text-green-600">{sub.status}</span> &middot; {sub.billing_cycle}</p>
          {sub.current_period_end && <p className="text-sm text-gray-500">Renews: {new Date(sub.current_period_end).toLocaleDateString()}</p>}
          <button onClick={cancel} className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg">Cancel Subscription</button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans.map((plan) => (
            <div key={plan.id} className="bg-white p-6 rounded-lg border text-center hover:shadow-lg transition-shadow">
              <h3 className="text-xl font-bold mb-2">{plan.name}</h3>
              {plan.description && <p className="text-sm text-gray-500 mb-4">{plan.description}</p>}
              <div className="text-3xl font-bold text-blue-600 mb-1">${plan.price_monthly}<span className="text-sm font-normal text-gray-500">/mo</span></div>
              <div className="text-sm text-gray-500 mb-4">${plan.price_yearly}/year</div>
              {plan.max_students > 0 && <p className="text-sm text-gray-600 mb-4">Up to {plan.max_students} students</p>}
              <button onClick={() => subscribe(plan.id, 'monthly')} className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg">Subscribe</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SubscriptionPage;
