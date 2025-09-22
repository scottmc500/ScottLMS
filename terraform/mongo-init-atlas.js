// MongoDB Atlas initialization script for ScottLMS (Idempotent)
// This script can be run multiple times safely

db = db.getSiblingDB('scottlms');

print('🚀 Initializing ScottLMS database schema...');

// ========================================
// CREATE COLLECTIONS WITH VALIDATION (IDEMPOTENT)
// ========================================

// Users collection
if (!db.getCollectionNames().includes('users')) {
  print('📝 Creating users collection...');
  db.createCollection('users', {
    validator: {
      $jsonSchema: {
        bsonType: 'object',
        required: ['email', 'username', 'role'],
        properties: {
          email: {
            bsonType: 'string',
            pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
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
  print('✅ Users collection created');
} else {
  print('✅ Users collection already exists');
}

// Courses collection
if (!db.getCollectionNames().includes('courses')) {
  print('📝 Creating courses collection...');
  db.createCollection('courses', {
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
  print('✅ Courses collection created');
} else {
  print('✅ Courses collection already exists');
}

// Enrollments collection
if (!db.getCollectionNames().includes('enrollments')) {
  print('📝 Creating enrollments collection...');
  db.createCollection('enrollments', {
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
  print('✅ Enrollments collection created');
} else {
  print('✅ Enrollments collection already exists');
}

// ========================================
// CREATE INDEXES (IDEMPOTENT)
// ========================================

print('🔍 Creating indexes...');

// Users indexes
try {
  db.users.createIndex({ 'email': 1 }, { unique: true, background: true });
  print('✅ Users email index created');
} catch (e) {
  if (e.code === 85) { // Index already exists
    print('✅ Users email index already exists');
  } else {
    print(`❌ Error creating users email index: ${e.message}`);
  }
}

try {
  db.users.createIndex({ 'username': 1 }, { unique: true, background: true });
  print('✅ Users username index created');
} catch (e) {
  if (e.code === 85) {
    print('✅ Users username index already exists');
  } else {
    print(`❌ Error creating users username index: ${e.message}`);
  }
}

// Courses indexes
try {
  db.courses.createIndex({ 'instructor_id': 1 }, { background: true });
  print('✅ Courses instructor_id index created');
} catch (e) {
  if (e.code === 85) {
    print('✅ Courses instructor_id index already exists');
  } else {
    print(`❌ Error creating courses instructor_id index: ${e.message}`);
  }
}

try {
  db.courses.createIndex({ 'title': 'text', 'description': 'text' }, { background: true });
  print('✅ Courses text search index created');
} catch (e) {
  if (e.code === 85) {
    print('✅ Courses text search index already exists');
  } else {
    print(`❌ Error creating courses text search index: ${e.message}`);
  }
}

// Enrollments indexes
try {
  db.enrollments.createIndex({ 'user_id': 1, 'course_id': 1 }, { unique: true, background: true });
  print('✅ Enrollments user_id+course_id index created');
} catch (e) {
  if (e.code === 85) {
    print('✅ Enrollments user_id+course_id index already exists');
  } else {
    print(`❌ Error creating enrollments user_id+course_id index: ${e.message}`);
  }
}

try {
  db.enrollments.createIndex({ 'course_id': 1 }, { background: true });
  print('✅ Enrollments course_id index created');
} catch (e) {
  if (e.code === 85) {
    print('✅ Enrollments course_id index already exists');
  } else {
    print(`❌ Error creating enrollments course_id index: ${e.message}`);
  }
}

// ========================================
// CREATE ADMIN USER (IDEMPOTENT)
// ========================================

print('👤 Creating admin user...');

const adminUser = {
  email: "admin@scottlms.com",
  username: "admin",
  first_name: "Scott",
  last_name: "Administrator",
  role: "admin",
  hashed_password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj5J1.9K.9K.", // "admin123"
  is_active: true,
  created_at: new Date(),
  updated_at: new Date()
};

const result = db.users.updateOne(
  { email: adminUser.email },
  { $set: adminUser },
  { upsert: true }
);

if (result.upsertedCount > 0) {
  print('✅ Admin user created');
} else {
  print('✅ Admin user already exists');
}

// ========================================
// VERIFY SETUP
// ========================================

print('\n🔍 Verifying database setup...');

const collections = db.getCollectionNames();
print(`📋 Collections: ${collections.join(', ')}`);

const userCount = db.users.countDocuments();
const courseCount = db.courses.countDocuments();
const enrollmentCount = db.enrollments.countDocuments();

print(`📊 Current data:`);
print(`   👥 Users: ${userCount}`);
print(`   📚 Courses: ${courseCount}`);
print(`   📝 Enrollments: ${enrollmentCount}`);

// Check indexes
print('\n🔍 Index status:');
const userIndexes = db.users.getIndexes().length;
const courseIndexes = db.courses.getIndexes().length;
const enrollmentIndexes = db.enrollments.getIndexes().length;

print(`   👥 Users indexes: ${userIndexes}`);
print(`   📚 Courses indexes: ${courseIndexes}`);
print(`   📝 Enrollments indexes: ${enrollmentIndexes}`);

print('\n🎉 Database initialization completed successfully!');
print('🚀 ScottLMS is ready for production use!');

// ========================================
// PRODUCTION NOTES
// ========================================

print('\n📝 Production Notes:');
print('   • Admin credentials: admin@scottlms.com / admin123');
print('   • Change default admin password after first login');
print('   • Database schema validation is enabled');
print('   • All indexes are created with background: true');
print('   • Script is idempotent - safe to run multiple times');
