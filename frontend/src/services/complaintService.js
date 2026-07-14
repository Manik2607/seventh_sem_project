export const complaintService = {
  fetchComplaints: () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          {
            id: 'c1',
            title: 'Pothole on Main Street',
            description: 'There is a large pothole near the intersection of 5th Ave and Main Street.',
            status: 'Pending',
            location: { latitude: 37.78825, longitude: -122.4324 },
            createdAt: '2026-07-07T10:00:00Z',
          },
          {
            id: 'c2',
            title: 'Streetlight Broken',
            description: 'Streetlight is flickering and mostly dark at night.',
            status: 'In Progress',
            location: { latitude: 37.78925, longitude: -122.4334 },
            createdAt: '2026-07-06T18:30:00Z',
          },
        ]);
      }, 1000);
    });
  },
  createComplaint: (complaintData) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          id: `c${Date.now()}`,
          ...complaintData,
          status: 'Pending',
          createdAt: new Date().toISOString(),
        });
      }, 1000);
    });
  },
};

export default complaintService;
