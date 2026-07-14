import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  complaints: [],
  loading: false,
  error: null,
};

const complaintSlice = createSlice({
  name: 'complaints',
  initialState,
  reducers: {
    fetchComplaintsStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    fetchComplaintsSuccess: (state, action) => {
      state.loading = false;
      state.complaints = action.payload;
    },
    fetchComplaintsFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
    addComplaint: (state, action) => {
      state.complaints.unshift(action.payload);
    },
  },
});

export const {
  fetchComplaintsStart,
  fetchComplaintsSuccess,
  fetchComplaintsFailure,
  addComplaint,
} = complaintSlice.actions;

export default complaintSlice.reducer;
