// MongoDB initialization script for ScottLMS with bcrypt password hashing
const { MongoClient, ObjectId } = require('mongodb');
const bcrypt = require('bcrypt');

async function initDatabase() {
    console.log('🚀 Starting ScottLMS MongoDB initialization...');
    
    const client = new MongoClient(process.env.MONGODB_URL);
    
    try {
        await client.connect();
        console.log('✅ Connected to MongoDB');
        
        const db = client.db('scottlms');
        
        // Create collections with validation
        console.log('📋 Creating collections with validation...');
        
        // Users collection
        await db.createCollection('users', {
            validator: {
                $jsonSchema: {
                    bsonType: 'object',
                    required: ['email', 'username', 'role'],
                    properties: {
                        email: {
                            bsonType: 'string',
                            pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
                        },
                        username: {
                            bsonType: 'string',
                            minLength: 3,
                            maxLength: 50
                        },
                        role: {
                            bsonType: 'string',
                            enum: ['student', 'instructor', 'admin']
                        }
                    }
                }
            }
        });
        
        // Courses collection
        await db.createCollection('courses', {
            validator: {
                $jsonSchema: {
                    bsonType: 'object',
                    required: ['title', 'description', 'instructor_id'],
                    properties: {
                        title: {
                            bsonType: 'string',
                            minLength: 1,
                            maxLength: 200
                        },
                        description: {
                            bsonType: 'string',
                            minLength: 1,
                            maxLength: 1000
                        },
                        instructor_id: {
                            bsonType: 'objectId'
                        }
                    }
                }
            }
        });
        
        // Enrollments collection
        await db.createCollection('enrollments', {
            validator: {
                $jsonSchema: {
                    bsonType: 'object',
                    required: ['user_id', 'course_id', 'enrolled_at'],
                    properties: {
                        user_id: {
                            bsonType: 'objectId'
                        },
                        course_id: {
                            bsonType: 'objectId'
                        },
                        enrolled_at: {
                            bsonType: 'date'
                        }
                    }
                }
            }
        });
        
        // Create indexes for better performance
        console.log('🔍 Creating indexes...');
        await db.collection('users').createIndex({ 'email': 1 }, { unique: true });
        await db.collection('users').createIndex({ 'username': 1 }, { unique: true });
        await db.collection('courses').createIndex({ 'instructor_id': 1 });
        await db.collection('courses').createIndex({ 'title': 'text', 'description': 'text' });
        await db.collection('enrollments').createIndex({ 'user_id': 1, 'course_id': 1 }, { unique: true });
        await db.collection('enrollments').createIndex({ 'course_id': 1 });
        
        // Generate bcrypt hashes
        console.log('🔐 Generating secure password hashes...');
        const adminHash = await bcrypt.hash('admin123', 12);
        const instructorHash = await bcrypt.hash('instructor123', 12);
        const studentHash = await bcrypt.hash('student123', 12);
        
        // Generate ObjectIds for referential integrity
        const adminId = new ObjectId();
        const instructorIds = [new ObjectId(), new ObjectId(), new ObjectId()];
        const studentIds = Array.from({length: 8}, () => new ObjectId());
        const courseIds = Array.from({length: 6}, () => new ObjectId());
        
        // Current timestamp
        const now = new Date();
        const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        const fiveDaysAgo = new Date(now.getTime() - 5 * 24 * 60 * 60 * 1000);
        const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        
        // Create users with real bcrypt hashes
        console.log('👥 Creating sample users...');
        
        // Admin user
        await db.collection('users').insertOne({
            _id: adminId,
            email: "admin@scottlms.com",
            username: "admin",
            first_name: "Scott",
            last_name: "Administrator",
            role: "admin",
            hashed_password: adminHash,
            is_active: true,
            created_at: now,
            updated_at: now
        });
        
        // Instructors
        const instructors = [
            { email: "john.smith@scottlms.com", username: "jsmith", first_name: "John", last_name: "Smith" },
            { email: "sarah.johnson@scottlms.com", username: "sjohnson", first_name: "Sarah", last_name: "Johnson" },
            { email: "mike.davis@scottlms.com", username: "mdavis", first_name: "Mike", last_name: "Davis" }
        ];
        
        for (let i = 0; i < instructors.length; i++) {
            await db.collection('users').insertOne({
                _id: instructorIds[i],
                email: instructors[i].email,
                username: instructors[i].username,
                first_name: instructors[i].first_name,
                last_name: instructors[i].last_name,
                role: "instructor",
                hashed_password: instructorHash,
                is_active: true,
                created_at: now,
                updated_at: now
            });
        }
        
        // Students
        const students = [
            { email: "alice.brown@student.com", username: "abrown", first_name: "Alice", last_name: "Brown" },
            { email: "bob.wilson@student.com", username: "bwilson", first_name: "Bob", last_name: "Wilson" },
            { email: "carol.garcia@student.com", username: "cgarcia", first_name: "Carol", last_name: "Garcia" },
            { email: "david.martinez@student.com", username: "dmartinez", first_name: "David", last_name: "Martinez" },
            { email: "emma.taylor@student.com", username: "etaylor", first_name: "Emma", last_name: "Taylor" },
            { email: "frank.anderson@student.com", username: "fanderson", first_name: "Frank", last_name: "Anderson" },
            { email: "grace.thomas@student.com", username: "gthomas", first_name: "Grace", last_name: "Thomas" },
            { email: "henry.jackson@student.com", username: "hjackson", first_name: "Henry", last_name: "Jackson" }
        ];
        
        for (let i = 0; i < students.length; i++) {
            await db.collection('users').insertOne({
                _id: studentIds[i],
                email: students[i].email,
                username: students[i].username,
                first_name: students[i].first_name,
                last_name: students[i].last_name,
                role: "student",
                hashed_password: studentHash,
                is_active: true,
                created_at: now,
                updated_at: now
            });
        }
        
        console.log(`✅ Created ${1 + instructors.length + students.length} users`);
        
        // Create courses
        console.log('📚 Creating sample courses...');
        
        const courses = [
            {
                _id: courseIds[0],
                title: "Introduction to Python Programming",
                description: "Learn the fundamentals of Python programming including variables, functions, loops, and object-oriented programming concepts.",
                instructor_id: instructorIds[0],
                status: "published",
                price: 99.99,
                duration_hours: 40,
                max_students: 25,
                tags: ["programming", "python", "beginner"],
                enrollment_count: 5,
                created_at: now,
                updated_at: now
            },
            {
                _id: courseIds[1],
                title: "Advanced Web Development with React",
                description: "Master modern web development using React, including hooks, state management, routing, and deployment strategies.",
                instructor_id: instructorIds[1],
                status: "published",
                price: 149.99,
                duration_hours: 60,
                max_students: 20,
                tags: ["web development", "react", "javascript", "advanced"],
                enrollment_count: 3,
                created_at: now,
                updated_at: now
            },
            {
                _id: courseIds[2],
                title: "Data Science Fundamentals",
                description: "Explore data science concepts including statistics, data visualization, machine learning basics, and Python libraries like pandas and matplotlib.",
                instructor_id: instructorIds[2],
                status: "published",
                price: 199.99,
                duration_hours: 80,
                max_students: 15,
                tags: ["data science", "statistics", "machine learning", "python"],
                enrollment_count: 3,
                created_at: now,
                updated_at: now
            },
            {
                _id: courseIds[3],
                title: "Database Design and SQL",
                description: "Learn database design principles, normalization, and master SQL queries for data retrieval and manipulation.",
                instructor_id: instructorIds[0],
                status: "published",
                price: 79.99,
                duration_hours: 30,
                max_students: 30,
                tags: ["database", "sql", "design", "intermediate"],
                enrollment_count: 4,
                created_at: now,
                updated_at: now
            },
            {
                _id: courseIds[4],
                title: "Mobile App Development with Flutter",
                description: "Build cross-platform mobile applications using Flutter and Dart programming language.",
                instructor_id: instructorIds[1],
                status: "draft",
                price: 179.99,
                duration_hours: 50,
                max_students: 18,
                tags: ["mobile", "flutter", "dart", "cross-platform"],
                enrollment_count: 0,
                created_at: now,
                updated_at: now
            },
            {
                _id: courseIds[5],
                title: "Cybersecurity Essentials",
                description: "Understanding cybersecurity threats, protection strategies, and best practices for secure software development.",
                instructor_id: instructorIds[2],
                status: "published",
                price: 129.99,
                duration_hours: 35,
                max_students: 22,
                tags: ["cybersecurity", "security", "networking", "intermediate"],
                enrollment_count: 3,
                created_at: now,
                updated_at: now
            }
        ];
        
        await db.collection('courses').insertMany(courses);
        console.log(`✅ Created ${courses.length} courses`);
        
        // Create enrollments
        console.log('📝 Creating sample enrollments...');
        
        const enrollments = [
            // Python course enrollments (popular course)
            { user_id: studentIds[0], course_id: courseIds[0], status: "active", progress: 75.0, enrolled_at: thirtyDaysAgo, last_accessed: oneDayAgo },
            { user_id: studentIds[1], course_id: courseIds[0], status: "completed", progress: 100.0, enrolled_at: thirtyDaysAgo, completed_at: fiveDaysAgo, last_accessed: fiveDaysAgo },
            { user_id: studentIds[2], course_id: courseIds[0], status: "active", progress: 45.0, enrolled_at: thirtyDaysAgo, last_accessed: oneDayAgo },
            { user_id: studentIds[3], course_id: courseIds[0], status: "active", progress: 20.0, enrolled_at: thirtyDaysAgo, last_accessed: oneDayAgo },
            { user_id: studentIds[4], course_id: courseIds[0], status: "active", progress: 90.0, enrolled_at: thirtyDaysAgo, last_accessed: oneDayAgo },
            
            // React course enrollments
            { user_id: studentIds[1], course_id: courseIds[1], status: "active", progress: 60.0, enrolled_at: thirtyDaysAgo, last_accessed: oneDayAgo },
            { user_id: studentIds[4], course_id: courseIds[1], status: "active", progress: 30.0, enrolled_at: thirtyDaysAgo, last_accessed: oneDayAgo },
            { user_id: studentIds[5], course_id: courseIds[1], status: "active", progress: 15.0, enrolled_at: thirtyDaysAgo, last_accessed: oneDayAgo },
            
            // Data Science course enrollments
            { user_id: studentIds[2], course_id: courseIds[2], status: "active", progress: 40.0, enrolled_at: thirtyDaysAgo, last_accessed: oneDayAgo },
            { user_id: studentIds[6], course_id: courseIds[2], status: "active", progress: 85.0, enrolled_at: thirtyDaysAgo, last_accessed: oneDayAgo },
            { user_id: studentIds[7], course_id: courseIds[2], status: "dropped", progress: 10.0, enrolled_at: thirtyDaysAgo, last_accessed: null },
            
            // SQL course enrollments
            { user_id: studentIds[0], course_id: courseIds[3], status: "completed", progress: 100.0, enrolled_at: thirtyDaysAgo, completed_at: fiveDaysAgo, last_accessed: fiveDaysAgo },
            { user_id: studentIds[3], course_id: courseIds[3], status: "active", progress: 55.0, enrolled_at: thirtyDaysAgo, last_accessed: oneDayAgo },
            { user_id: studentIds[5], course_id: courseIds[3], status: "active", progress: 25.0, enrolled_at: thirtyDaysAgo, last_accessed: oneDayAgo },
            { user_id: studentIds[7], course_id: courseIds[3], status: "active", progress: 70.0, enrolled_at: thirtyDaysAgo, last_accessed: oneDayAgo },
            
            // Cybersecurity course enrollments
            { user_id: studentIds[1], course_id: courseIds[5], status: "active", progress: 35.0, enrolled_at: thirtyDaysAgo, last_accessed: oneDayAgo },
            { user_id: studentIds[4], course_id: courseIds[5], status: "active", progress: 50.0, enrolled_at: thirtyDaysAgo, last_accessed: oneDayAgo },
            { user_id: studentIds[6], course_id: courseIds[5], status: "active", progress: 80.0, enrolled_at: thirtyDaysAgo, last_accessed: oneDayAgo }
        ];
        
        await db.collection('enrollments').insertMany(enrollments);
        console.log(`✅ Created ${enrollments.length} enrollments`);
        
        console.log('🎉 ScottLMS database initialization completed successfully!');
        console.log('📊 Summary:');
        console.log(`   👥 Users: ${1 + instructors.length + students.length} (1 admin, ${instructors.length} instructors, ${students.length} students)`);
        console.log(`   📚 Courses: ${courses.length} (${courses.filter(c => c.status === 'published').length} published, ${courses.filter(c => c.status === 'draft').length} draft)`);
        console.log(`   📝 Enrollments: ${enrollments.length}`);
        console.log('🔐 All passwords are securely hashed with bcrypt!');
        console.log('🚀 Ready for testing!');
        
        // Display login credentials
        console.log('\n🔑 Login Credentials:');
        console.log('   Admin: admin@scottlms.com / admin123');
        console.log('   Instructor: john.smith@scottlms.com / instructor123');
        console.log('   Student: alice.brown@student.com / student123');
        
    } catch (error) {
        console.error('❌ Error during database initialization:', error);
        throw error;
    } finally {
        await client.close();
        console.log('🔌 Database connection closed');
    }
}

// Run the initialization
initDatabase().catch((error) => {
    console.error('💥 Fatal error:', error);
    process.exit(1);
});
