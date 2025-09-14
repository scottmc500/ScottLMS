// MongoDB initialization script for ScottLMS
db = db.getSiblingDB('scottlms');

// Create collections with validation
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

db.createCollection('enrollments', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['student_id', 'course_id', 'enrollment_date'],
      properties: {
        student_id: {
          bsonType: 'objectId'
        },
        course_id: {
          bsonType: 'objectId'
        },
        enrollment_date: {
          bsonType: 'date'
        }
      }
    }
  }
});

// Create indexes for better performance
db.users.createIndex({ 'email': 1 }, { unique: true });
db.users.createIndex({ 'username': 1 }, { unique: true });
db.courses.createIndex({ 'instructor_id': 1 });
db.courses.createIndex({ 'title': 'text', 'description': 'text' });
db.enrollments.createIndex({ 'student_id': 1, 'course_id': 1 }, { unique: true });
db.enrollments.createIndex({ 'course_id': 1 });

print('ScottLMS database initialized successfully!');
