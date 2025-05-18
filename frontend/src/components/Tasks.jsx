import React from 'react';

const columns = [
  // ... other columns ...
  {
    accessorKey: 'assigned_to',
    header: 'Volunteer Assigned',
    Cell: ({ cell, row }) => {
      const assigned = row.original.assigned_to;
      // If assigned_to is an object with a name, display the name
      if (assigned && typeof assigned === 'object' && assigned.name) {
        return assigned.name;
      }
      // If for some reason it's just a string (shouldn't be after backend update), show as is
      return assigned || '-';
    },
  },
  // ... other columns ...
];

const Tasks = () => <div>all task</div>;
export default Tasks;
