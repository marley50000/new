// Initialize Supabase client (replace with your actual keys)
// It's generally recommended to handle keys more securely in a backend or environment variables
const supabaseUrl = 'https://qzddjvloicjwshggzctt.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF6ZGRqdmxvaWNqd3NoZ2d6Y3R0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk0MDk5MzMsImV4cCI6MjA2NDk4NTkzM30.mkrERrCanIkNnIlch5UJ-OOJ9az7oXs1EFZijkf7y7o';
const supabase = window.supabase.createClient(supabaseUrl, supabaseKey);

// Function to fetch and display user's requests
async function fetchUserRequests() {
  const { data: { session }, error: sessionError } = await supabase.auth.getSession();

  if (sessionError) {
    console.error('Error fetching session:', sessionError.message);
    return;
  }

  if (!session) {
    // User is not logged in. The inline script should handle the redirect,
    // but we'll log a message here.
    console.log('No active session found. Cannot fetch requests.');
    // Optionally clear the requests list or show a message
    const requestsListDiv = document.getElementById('userRequestsList');
    if (requestsListDiv) {
        requestsListDiv.innerHTML = '<p class="text-gray-600">Please log in to view your requests.</p>';
    }
    return;
  }

  const userId = session.user.id;
  const { data: requests, error } = await supabase
    .from('requests') // Assuming your table is named 'requests'
    .select('id, description, created_at') // Select relevant columns
    .eq('user_id', userId) // Filter by the current user's ID
    .order('created_at', { ascending: false }); // Order by creation date

  if (error) {
    console.error('Error fetching user requests:', error.message);
    const requestsListDiv = document.getElementById('userRequestsList');
    if (requestsListDiv) {
        requestsListDiv.innerHTML = '<p class="text-red-500">Error loading requests.</p>';
    }
  } else {
    displayRequests(requests);
  }
}

// Function to display requests in the HTML
function displayRequests(requests) {
  const requestsListDiv = document.getElementById('userRequestsList');
  if (!requestsListDiv) return; // Exit if the container doesn't exist

  requestsListDiv.innerHTML = ''; // Clear current list

  if (requests.length === 0) {
    requestsListDiv.innerHTML = '<p class="text-gray-600">You have no active requests yet.</p>';
    return;
  }

  requests.forEach(request => {
    const requestElement = document.createElement('div');
    requestElement.className = 'bg-[#f7f9fc] rounded-lg p-4 shadow-sm'; // Tailwind classes for styling
    requestElement.innerHTML = `
      <p class="text-gray-800 text-sm">${request.description}</p>
      <p class="text-gray-500 text-xs mt-2">Posted: ${new Date(request.created_at).toLocaleString()}</p>
      <!-- Add more details or actions here if needed -->
    `;
    requestsListDiv.appendChild(requestElement);
  });
}

// Function to handle posting a new request
async function postRequest(description) {
  const { data: { session }, error: sessionError } = await supabase.auth.getSession();

  if (sessionError || !session) {
    console.error('User not logged in to post request.');
    alert('Please log in to post a request.');
    // Redirect is handled by the inline script, but this provides feedback
    return;
  }

  const userId = session.user.id;
  // Assuming your table is named 'requests' and has 'user_id' and 'description' columns
  const { data, error } = await supabase
    .from('requests')
    .insert([
      { user_id: userId, description: description }
    ])
    .select(); // Use .select() to get the inserted row data if needed

  if (error) {
    console.error('Error posting request:', error.message);
    alert('Failed to post request: ' + error.message);
  } else {
    console.log('Request posted successfully:', data);
    alert('Request posted successfully!');
    document.getElementById('requestDescription').value = ''; // Clear the textarea
    fetchUserRequests(); // Refresh the list of requests
  }
}

// Event listener for the request form submission
document.getElementById('requestForm')?.addEventListener('submit', async (event) => {
  event.preventDefault(); // Prevent default form submission

  const requestDescriptionElement = document.getElementById('requestDescription');
  const requestDescription = requestDescriptionElement ? requestDescriptionElement.value.trim() : '';


  if (requestDescription) {
    await postRequest(requestDescription);
  } else {
    alert('Please enter a description for your request.');
  }
});

// Event listener for the logout button
document.getElementById('logout-button')?.addEventListener('click', async () => {
  const { error } = await supabase.auth.signOut();
  if (error) {
    console.error('Logout error:', error.message);
    alert("Logout Error: " + error.message);
  } else {
    // Redirect to login or home page after successful logout
    window.location.href = 'auth.html';
  }
});


// Initial fetch of requests when the page loads
document.addEventListener('DOMContentLoaded', () => {
  // The inline script block handles the initial session check and redirect.
  // If we are on this page, a session should exist.
  // We call fetchUserRequests which also checks for a session internally.
  fetchUserRequests();

  // Add event listeners for other elements like category buttons or search form here if needed
  // Example:
  // document.getElementById('searchForm')?.addEventListener('submit', (event) => {
  //   event.preventDefault();
  //   // Implement search logic here
  //   const searchTerm = document.getElementById('searchInput').value;
  //   console.log('Searching for:', searchTerm);
  //   // Call a function to perform the search and update results
  // });
});