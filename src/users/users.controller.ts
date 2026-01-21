import { Body, Controller, Post } from '@nestjs/common';
import * as bcrypt from 'bcrypt';
import { UsersService } from './users.service';

export interface registry {
  username: string;
  email: string;
  password: string;
}
@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}
  @Post('register')
  async register(@Body() body: registry) {
    const savedUser = await this.usersService.create(
      body.username,
      body.password,
    );
    return {
      message: 'User register successfully',
      usere: savedUser,
    };
  }

  @Post('login')
  async login(@Body() body: registry) {
    const user = await this.usersService.findOne(body.username);
    if (!user) return { message: 'User not found' };

    const isMatch = await bcrypt.compare(body.password, user.password);

    if (isMatch) {
      return {
        message: 'Login successful!',
        token: 'Sample_token',
      };
    } else {
      return { message: 'Wrong password!' };
    }
  }
}
