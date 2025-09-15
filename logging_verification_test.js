#!/usr/bin/env node
/**
 * Comprehensive Logging Verification Test
 * =====================================
 * 
 * This script verifies that the enhanced logging system is working
 * correctly across the entire PII Scanner application.
 */

const https = require('https');

class LoggingVerificationTester {
    constructor() {
        this.baseUrl = 'https://pii-dashboard.preview.emergentagent.com';
        this.results = {
            backend_health: false,
            error_endpoint: false,
            classify_endpoint: false,
            frontend_accessible: false
        };
    }

    async makeRequest(url, options = {}) {
        return new Promise((resolve, reject) => {
            const req = https.request(url, options, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    resolve({
                        statusCode: res.statusCode,
                        headers: res.headers,
                        data: data
                    });
                });
            });
            
            req.on('error', reject);
            
            if (options.body) {
                req.write(options.body);
            }
            
            req.end();
        });
    }

    async testBackendHealth() {
        console.log('🏥 Testing Backend Health...');
        try {
            const response = await this.makeRequest(`${this.baseUrl}/api/health`);
            
            if (response.statusCode === 200) {
                const healthData = JSON.parse(response.data);
                console.log(`✅ Backend Health: ${healthData.status}`);
                console.log(`   Version: ${healthData.version}`);
                console.log(`   Logging: ${healthData.components.logging ? 'Enabled' : 'Disabled'}`);
                this.results.backend_health = true;
                return true;
            } else {
                console.log(`❌ Backend Health Check Failed: ${response.statusCode}`);
                return false;
            }
        } catch (error) {
            console.log(`❌ Backend Health Check Error: ${error.message}`);
            return false;
        }
    }

    async testErrorEndpoint() {
        console.log('🚨 Testing Frontend Error Logging Endpoint...');
        try {
            const testError = {
                timestamp: new Date().toISOString(),
                level: 'ERROR',
                message: 'Test frontend error from verification script',
                sessionId: 'verification-test-session',
                url: '/test'
            };

            const response = await this.makeRequest(`${this.baseUrl}/api/log-frontend-error`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(testError)
            });

            if (response.statusCode === 200) {
                const result = JSON.parse(response.data);
                console.log(`✅ Error Endpoint Working: Error ID ${result.error_id}`);
                console.log(`   Status: ${result.status}`);
                this.results.error_endpoint = true;
                return true;
            } else {
                console.log(`❌ Error Endpoint Failed: ${response.statusCode}`);
                console.log(`   Response: ${response.data}`);
                return false;
            }
        } catch (error) {
            console.log(`❌ Error Endpoint Test Failed: ${error.message}`);
            return false;
        }
    }

    async testClassifyEndpoint() {
        console.log('🔍 Testing Classification Endpoint...');
        try {
            const classifyRequest = {
                session_id: 'verification-test-session',
                selected_fields: [
                    { table_name: 'users', column_name: 'email', data_type: 'VARCHAR' },
                    { table_name: 'users', column_name: 'first_name', data_type: 'VARCHAR' }
                ],
                regulations: ['GDPR']
            };

            const response = await this.makeRequest(`${this.baseUrl}/api/classify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(classifyRequest)
            });

            if (response.statusCode === 200) {
                const result = JSON.parse(response.data);
                console.log(`✅ Classification Endpoint Working`);
                console.log(`   Fields Processed: ${result.results?.summary?.total_fields || 0}`);
                console.log(`   Processing Time: ${result.processing_time}`);
                this.results.classify_endpoint = true;
                return true;
            } else {
                console.log(`❌ Classification Endpoint Failed: ${response.statusCode}`);
                return false;
            }
        } catch (error) {
            console.log(`❌ Classification Endpoint Test Failed: ${error.message}`);
            return false;
        }
    }

    async testFrontendAccess() {
        console.log('🌐 Testing Frontend Access...');
        try {
            const response = await this.makeRequest(this.baseUrl);
            
            if (response.statusCode === 200 && response.data.includes('PII Scanner')) {
                console.log('✅ Frontend Accessible');
                this.results.frontend_accessible = true;
                return true;
            } else {
                console.log(`❌ Frontend Access Failed: ${response.statusCode}`);
                return false;
            }
        } catch (error) {
            console.log(`❌ Frontend Access Test Failed: ${error.message}`);
            return false;
        }
    }

    async runAllTests() {
        console.log('🧪 Starting Comprehensive Logging Verification Tests');
        console.log('='.repeat(60));

        await this.testBackendHealth();
        await this.testErrorEndpoint();
        await this.testClassifyEndpoint();
        await this.testFrontendAccess();

        console.log('\n📊 Test Results Summary:');
        console.log('='.repeat(60));

        const passedTests = Object.values(this.results).filter(Boolean).length;
        const totalTests = Object.keys(this.results).length;

        Object.entries(this.results).forEach(([test, passed]) => {
            console.log(`   ${passed ? '✅' : '❌'} ${test.replace(/_/g, ' ')}: ${passed ? 'PASS' : 'FAIL'}`);
        });

        console.log(`\n🎯 Overall Result: ${passedTests}/${totalTests} tests passed`);

        if (passedTests === totalTests) {
            console.log('🎉 All logging integration tests PASSED! System ready for debugging.');
        } else {
            console.log('⚠️ Some tests failed. Enhanced logging may have issues.');
        }

        return passedTests === totalTests;
    }
}

// Run the tests
const tester = new LoggingVerificationTester();
tester.runAllTests().then(success => {
    process.exit(success ? 0 : 1);
}).catch(error => {
    console.error('❌ Test execution failed:', error);
    process.exit(1);
});