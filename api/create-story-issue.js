// Serverless function to securely create GitHub issues for story submissions
// This protects the GitHub token from being exposed in client-side code

export default async function handler(req, res) {
    // Only allow POST requests
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    // Enable CORS for the frontend
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    // Handle preflight request
    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    try {
        const { title, body, labels } = req.body;

        // Validate required fields
        if (!title || !body) {
            return res.status(400).json({
                error: 'Missing required fields: title and body are required'
            });
        }

        // Get GitHub token from environment variable
        const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
        if (!GITHUB_TOKEN) {
            console.error('GITHUB_TOKEN environment variable not set');
            return res.status(500).json({
                error: 'Server configuration error'
            });
        }

        // Create GitHub issue
        const response = await fetch('https://api.github.com/repos/patruff/rufftree/issues', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${GITHUB_TOKEN}`,
                'Content-Type': 'application/json',
                'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': '2022-11-28',
                'User-Agent': 'RuffTree-Story-Submission'
            },
            body: JSON.stringify({
                title,
                body,
                labels: labels || ['family-story', 'story:pending']
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('GitHub API error:', errorData);
            return res.status(response.status).json({
                error: 'Failed to create GitHub issue',
                details: errorData.message
            });
        }

        const issue = await response.json();

        return res.status(201).json({
            success: true,
            issueUrl: issue.html_url,
            issueNumber: issue.number
        });

    } catch (error) {
        console.error('Error creating story issue:', error);
        return res.status(500).json({
            error: 'Internal server error',
            message: error.message
        });
    }
}
