import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8080';

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const url = `${BACKEND_URL}/api/${path}${request.nextUrl.search}`;
  
  try {
    const headers: Record<string, string> = {};
    
    const cookieHeader = request.headers.get('cookie');
    if (cookieHeader) {
      headers['cookie'] = cookieHeader;
    }
    
    const authHeader = request.headers.get('authorization');
    if (authHeader) {
      headers['authorization'] = authHeader;
    }
    
    const backendResponse = await fetch(url, {
      method: 'GET',
      headers,
      credentials: 'include',
    });
    
    const responseHeaders = new Headers();
    backendResponse.headers.forEach((value, key) => {
      responseHeaders.set(key, value);
    });
    
    if (backendResponse.status === 204 || backendResponse.headers.get('content-length') === '0') {
      return new NextResponse(null, {
        status: backendResponse.status,
        headers: responseHeaders,
      });
    }
    
    const contentType = backendResponse.headers.get('content-type') || '';
    
    if (contentType.includes('application/json')) {
      const data = await backendResponse.json();
      return NextResponse.json(data, {
        status: backendResponse.status,
        headers: responseHeaders,
      });
    } else {
      const body = await backendResponse.arrayBuffer();
      return new NextResponse(body, {
        status: backendResponse.status,
        headers: responseHeaders,
      });
    }
  } catch (error) {
    console.error('[Proxy GET Error]', error);
    return NextResponse.json(
      { error: 'Backend unavailable' },
      { status: 503 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const url = `${BACKEND_URL}/api/${path}`;
  
  try {
    const body = await request.json();
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    const cookieHeader = request.headers.get('cookie');
    if (cookieHeader) {
      headers['cookie'] = cookieHeader;
    }

    const authHeader = request.headers.get('authorization');
    if (authHeader) {
      headers['authorization'] = authHeader;
    }

    const backendResponse = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
      credentials: 'include',
    });
    
    const responseHeaders = new Headers();
    backendResponse.headers.forEach((value, key) => {
      responseHeaders.set(key, value);
    });
    
    if (backendResponse.status === 204 || backendResponse.headers.get('content-length') === '0') {
      return new NextResponse(null, {
        status: backendResponse.status,
        headers: responseHeaders,
      });
    }
    
    const contentType = backendResponse.headers.get('content-type') || '';
    
    if (contentType.includes('application/json')) {
      const data = await backendResponse.json();
      return NextResponse.json(data, {
        status: backendResponse.status,
        headers: responseHeaders,
      });
    } else {
      const body = await backendResponse.arrayBuffer();
      return new NextResponse(body, {
        status: backendResponse.status,
        headers: responseHeaders,
      });
    }
  } catch (error) {
    console.error('[Proxy POST Error]', error);
    return NextResponse.json(
      { error: 'Backend unavailable' },
      { status: 503 }
    );
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const url = `${BACKEND_URL}/api/${path}`;
  
  try {
    const body = await request.json();
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    const cookieHeader = request.headers.get('cookie');
    if (cookieHeader) {
      headers['cookie'] = cookieHeader;
    }

    const authHeader = request.headers.get('authorization');
    if (authHeader) {
      headers['authorization'] = authHeader;
    }

    const backendResponse = await fetch(url, {
      method: 'PUT',
      headers,
      body: JSON.stringify(body),
      credentials: 'include',
    });
    
    const responseHeaders = new Headers();
    backendResponse.headers.forEach((value, key) => {
      responseHeaders.set(key, value);
    });
    
    if (backendResponse.status === 204 || backendResponse.headers.get('content-length') === '0') {
      return new NextResponse(null, {
        status: backendResponse.status,
        headers: responseHeaders,
      });
    }
    
    const contentType = backendResponse.headers.get('content-type') || '';
    
    if (contentType.includes('application/json')) {
      const data = await backendResponse.json();
      return NextResponse.json(data, {
        status: backendResponse.status,
        headers: responseHeaders,
      });
    } else {
      const body = await backendResponse.arrayBuffer();
      return new NextResponse(body, {
        status: backendResponse.status,
        headers: responseHeaders,
      });
    }
  } catch (error) {
    console.error('[Proxy PUT Error]', error);
    return NextResponse.json(
      { error: 'Backend unavailable' },
      { status: 503 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const url = `${BACKEND_URL}/api/${path}`;
  
  try {
    const headers: Record<string, string> = {};

    const cookieHeader = request.headers.get('cookie');
    if (cookieHeader) {
      headers['cookie'] = cookieHeader;
    }

    const authHeader = request.headers.get('authorization');
    if (authHeader) {
      headers['authorization'] = authHeader;
    }

    const backendResponse = await fetch(url, {
      method: 'DELETE',
      headers,
      credentials: 'include',
    });
    
    const responseHeaders = new Headers();
    backendResponse.headers.forEach((value, key) => {
      responseHeaders.set(key, value);
    });
    
    if (backendResponse.status === 204 || backendResponse.headers.get('content-length') === '0') {
      return new NextResponse(null, {
        status: backendResponse.status,
        headers: responseHeaders,
      });
    }
    
    const contentType = backendResponse.headers.get('content-type') || '';
    
    if (contentType.includes('application/json')) {
      const data = await backendResponse.json();
      return NextResponse.json(data, {
        status: backendResponse.status,
        headers: responseHeaders,
      });
    } else {
      const body = await backendResponse.arrayBuffer();
      return new NextResponse(body, {
        status: backendResponse.status,
        headers: responseHeaders,
      });
    }
  } catch (error) {
    console.error('[Proxy DELETE Error]', error);
    return NextResponse.json(
      { error: 'Backend unavailable' },
      { status: 503 }
    );
  }
}
