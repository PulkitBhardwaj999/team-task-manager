export function LoadingSkeleton() {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="skeleton h-20 rounded-lg" />
      ))}
    </div>
  );
}

export function TaskSkeleton() {
  return (
    <div className="card p-4 space-y-3">
      <div className="skeleton h-4 w-3/4 rounded" />
      <div className="skeleton h-3 w-1/2 rounded" />
      <div className="flex gap-2">
        <div className="skeleton h-6 w-16 rounded-full" />
        <div className="skeleton h-6 w-16 rounded-full" />
      </div>
    </div>
  );
}

export function ProjectSkeleton() {
  return (
    <div className="card p-4 space-y-3">
      <div className="skeleton h-6 w-1/2 rounded" />
      <div className="skeleton h-4 w-full rounded" />
      <div className="skeleton h-4 w-3/4 rounded" />
      <div className="skeleton h-10 w-full rounded" />
    </div>
  );
}
